"""
Keep-Alive Manager - Sistema avançado de manutenção de conexão
Monitora múltiplos endpoints do GitHub e mantém a conexão ativa
"""

import asyncio
import logging
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import requests
import json

# Importar configurações
sys.path.insert(0, str(Path(__file__).parent))
from config import get_config, validate_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EndpointStatus:
    """Status de um endpoint."""
    url: str
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    is_healthy: bool = True


class KeepAliveManager:
    """
    Sistema avançado de keep-alive com monitoramento inteligente.
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.endpoints: Dict[str, EndpointStatus] = {}
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.callbacks: List[Callable] = []
        
        # Estatísticas
        self.total_checks = 0
        self.total_success = 0
        self.total_failures = 0
        self.start_time = None
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def add_callback(self, callback: Callable):
        """Adiciona callback para eventos de status."""
        self.callbacks.append(callback)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção."""
        logger.info(f"Recebido sinal {signum}, encerrando...")
        self.stop()
        sys.exit(0)
    
    async def start(self):
        """Inicia o sistema de keep-alive."""
        if not validate_config():
            logger.error("Configuração inválida, não é possível iniciar")
            return False
        
        logger.info("🚀 Iniciando Keep-Alive Manager")
        logger.info(f"Intervalo: {self.config.keep_alive['interval_seconds']}s")
        logger.info(f"Endpoints: {len(self.config.keep_alive['endpoints'])}")
        
        # Inicializar endpoints
        for url in self.config.keep_alive['endpoints']:
            self.endpoints[url] = EndpointStatus(url=url)
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar loop principal
        try:
            await self._main_loop()
        except KeyboardInterrupt:
            logger.info("Encerramento solicitado pelo usuário")
        finally:
            await self.stop()
        
        return True
    
    def start_sync(self):
        """Versão síncrona para execução standalone."""
        try:
            return asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Encerramento solicitado pelo usuário")
            return False
    
    def stop(self):
        """Para o sistema de keep-alive."""
        logger.info("🛑 Parando Keep-Alive Manager")
        self.is_running = False
        self.executor.shutdown(wait=True)
        self._save_stats()
    
    async def _main_loop(self):
        """Loop principal do keep-alive."""
        while self.is_running:
            try:
                await self._check_all_endpoints()
                await asyncio.sleep(self.config.keep_alive['interval_seconds'])
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(5)  # Pequeno delay antes de tentar novamente
    
    async def _check_all_endpoints(self):
        """Verifica todos os endpoints simultaneamente."""
        self.total_checks += 1
        
        # Criar tasks para todos os endpoints
        tasks = []
        for url, status in self.endpoints.items():
            task = asyncio.create_task(self._check_endpoint(url, status))
            tasks.append(task)
        
        # Aguardar todas as tasks completarem
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar saúde geral
        healthy_count = sum(1 for s in self.endpoints.values() if s.is_healthy)
        total_endpoints = len(self.endpoints)
        
        if healthy_count == 0:
            logger.warning("⚠️  Nenhum endpoint está saudável!")
            await self._trigger_alert("critical", "Todos os endpoints do GitHub estão offline")
        elif healthy_count < total_endpoints:
            logger.warning(f"⚠️  {total_endpoints - healthy_count}/{total_endpoints} endpoints offline")
        
        # Log resumo
        logger.info(f"✅ Check #{self.total_checks} - {healthy_count}/{total_endpoints} endpoints saudáveis")
    
    async def _check_endpoint(self, url: str, status: EndpointStatus):
        """Verifica um endpoint específico."""
        status.last_check = datetime.now()
        
        try:
            # Executar check em thread separada para não bloquear
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._sync_check_endpoint,
                url,
                status
            )
            
            if success:
                self.total_success += 1
                status.success_count += 1
                status.consecutive_failures = 0
                status.is_healthy = True
                logger.debug(f"✅ {url} - OK")
            else:
                self.total_failures += 1
                status.failure_count += 1
                status.consecutive_failures += 1
                status.is_healthy = False
                logger.warning(f"❌ {url} - Falhou ({status.consecutive_failures} falhas consecutivas)")
                
                # Alerta para falhas consecutivas
                if status.consecutive_failures >= 3:
                    await self._trigger_alert("warning", f"Endpoint {url} com {status.consecutive_failures} falhas consecutivas")
        
        except Exception as e:
            logger.error(f"💥 Erro ao checar {url}: {e}")
            status.failure_count += 1
            status.consecutive_failures += 1
            status.is_healthy = False
    
    def _sync_check_endpoint(self, url: str, status: EndpointStatus) -> bool:
        """Versão síncrona do check de endpoint."""
        try:
            # Aumentar timeout para 15 segundos e melhorar User-Agent
            response = requests.head(
                url,
                timeout=15,  # Aumentado de 10 para 15 segundos
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; MMECO-KeepAlive/1.0; +https://github.com/groovaloo/MMECO)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                },
                allow_redirects=True
            )
            
            success = response.status_code < 400
            if success:
                status.last_success = datetime.now()
            else:
                status.last_failure = datetime.now()
                logger.debug(f"Status {response.status_code} para {url}")
            
            return success
            
        except requests.exceptions.Timeout as e:
            status.last_failure = datetime.now()
            logger.debug(f"Timeout para {url}: {e}")
            return False
        except requests.exceptions.ConnectionError as e:
            status.last_failure = datetime.now()
            logger.debug(f"Erro de conexão para {url}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            status.last_failure = datetime.now()
            logger.debug(f"Erro geral para {url}: {e}")
            return False
    
    async def _trigger_alert(self, level: str, message: str):
        """Dispara alerta para callbacks registrados."""
        for callback in self.callbacks:
            try:
                await callback(level, message)
            except Exception as e:
                logger.error(f"Erro no callback de alerta: {e}")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do keep-alive."""
        uptime = datetime.now() - self.start_time if self.start_time else 0
        healthy_endpoints = sum(1 for s in self.endpoints.values() if s.is_healthy)
        
        return {
            'uptime': str(uptime),
            'total_checks': self.total_checks,
            'total_success': self.total_success,
            'total_failures': self.total_failures,
            'success_rate': (self.total_success / max(self.total_checks, 1)) * 100,
            'healthy_endpoints': healthy_endpoints,
            'total_endpoints': len(self.endpoints),
            'endpoints': {
                url: {
                    'success_count': status.success_count,
                    'failure_count': status.failure_count,
                    'consecutive_failures': status.consecutive_failures,
                    'is_healthy': status.is_healthy,
                    'last_check': status.last_check.isoformat() if status.last_check else None
                }
                for url, status in self.endpoints.items()
            }
        }
    
    def _save_stats(self):
        """Salva estatísticas em arquivo."""
        stats = self.get_stats()
        stats_file = self.config.keep_alive['log_file'].with_suffix('.stats.json')
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            logger.info(f"📊 Estatísticas salvas em: {stats_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
    
    def print_status(self):
        """Imprime status atual."""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📡 KEEP-ALIVE STATUS")
        print("="*60)
        print(f"Uptime: {stats['uptime']}")
        print(f"Total Checks: {stats['total_checks']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Endpoints Saudáveis: {stats['healthy_endpoints']}/{stats['total_endpoints']}")
        
        print("\n📋 ENDPOINTS:")
        for url, data in stats['endpoints'].items():
            status = "✅" if data['is_healthy'] else "❌"
            print(f"  {status} {url}")
            print(f"     Success: {data['success_count']}, Failures: {data['failure_count']}")
            if data['consecutive_failures'] > 0:
                print(f"     Consecutive Failures: {data['consecutive_failures']}")
        
        print("="*60)


def main():
    """Função principal para execução standalone."""
    manager = KeepAliveManager()
    
    # Callback para imprimir status a cada 10 checks
    check_count = 0
    async def status_callback(level, message):
        nonlocal check_count
        check_count += 1
        if check_count % 10 == 0:
            manager.print_status()
    
    manager.add_callback(status_callback)
    
    try:
        manager.start()
    except Exception as e:
        logger.error(f"Erro ao iniciar: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())