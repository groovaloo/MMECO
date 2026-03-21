"""
Alert System - Sistema de alertas inteligentes para erros e eventos críticos
Gerencia alertas por canais, prioridades e regras de disparo
"""

import asyncio
import logging
import json
import time
import sys
import inspect
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Importar configurações
sys.path.insert(0, str(Path(__file__).parent))
from config import get_config, validate_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Níveis de alerta."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """Canais de alerta."""
    LOG = "log"
    FILE = "file"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class AlertRule:
    """Regra de disparo de alerta."""
    name: str
    level: AlertLevel
    channels: List[AlertChannel]
    conditions: Dict[str, Any]
    cooldown_minutes: int = 5
    enabled: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class AlertEvent:
    """Evento de alerta."""
    level: AlertLevel
    message: str
    timestamp: datetime
    data: Dict[str, Any]
    rule_name: str
    channels: List[AlertChannel]


class AlertSystem:
    """
    Sistema de alertas inteligentes.
    Gerencia disparo de alertas baseado em regras e canais configuráveis.
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.rules: List[AlertRule] = []
        self.callbacks: List[Callable] = []
        self.alert_history: List[AlertEvent] = []
        self.cooldown_cache: Dict[str, datetime] = {}
        
        # Canais de alerta
        self.channels = {
            AlertChannel.LOG: self._send_log,
            AlertChannel.FILE: self._send_file,
            AlertChannel.EMAIL: self._send_email,
            AlertChannel.WEBHOOK: self._send_webhook,
            AlertChannel.CONSOLE: self._send_console
        }
        
        # Estatísticas
        self.stats = {
            'total_alerts': 0,
            'alerts_by_level': {level.value: 0 for level in AlertLevel},
            'alerts_by_channel': {channel.value: 0 for channel in AlertChannel},
            'last_alert_time': None
        }
        
        # Configurar regras padrão
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configura regras de alerta padrão."""
        default_rules = [
            AlertRule(
                name="new_errors_threshold",
                level=AlertLevel.WARNING,
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                conditions={
                    'type': 'new_errors',
                    'threshold': 5
                },
                cooldown_minutes=10
            ),
            AlertRule(
                name="build_failures",
                level=AlertLevel.CRITICAL,
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                conditions={
                    'type': 'build_failure',
                    'consecutive': 3
                },
                cooldown_minutes=5
            ),
            AlertRule(
                name="memory_low",
                level=AlertLevel.WARNING,
                channels=[AlertChannel.LOG],
                conditions={
                    'type': 'memory_usage',
                    'threshold_mb': 50
                },
                cooldown_minutes=30
            ),
            AlertRule(
                name="github_down",
                level=AlertLevel.EMERGENCY,
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                conditions={
                    'type': 'github_connectivity',
                    'consecutive_failures': 5
                },
                cooldown_minutes=15
            ),
            AlertRule(
                name="error_trend_increasing",
                level=AlertLevel.WARNING,
                channels=[AlertChannel.LOG],
                conditions={
                    'type': 'error_trend',
                    'direction': 'increasing',
                    'threshold': 20  # 20% increase
                },
                cooldown_minutes=60
            )
        ]
        
        self.rules.extend(default_rules)
        logger.info(f"✅ {len(default_rules)} regras de alerta padrão configuradas")
    
    def add_rule(self, rule: AlertRule):
        """Adiciona uma nova regra de alerta."""
        self.rules.append(rule)
        logger.info(f"➕ Regra adicionada: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove uma regra de alerta."""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"➖ Regra removida: {rule_name}")
    
    def add_callback(self, callback: Callable):
        """Adiciona callback para eventos de alerta."""
        self.callbacks.append(callback)
    
    async def trigger_alert(self, level: str, message: str, data: Optional[Dict] = None):
        """
        Dispara um alerta manualmente.
        
        Args:
            level: Nível do alerta (info, warning, critical, emergency)
            message: Mensagem do alerta
            data: Dados adicionais
        """
        try:
            alert_level = AlertLevel(level)
            channels = self._get_channels_for_level(alert_level)
            
            event = AlertEvent(
                level=alert_level,
                message=message,
                timestamp=datetime.now(),
                data=data or {},
                rule_name="manual",
                channels=channels
            )
            
            await self._process_alert(event)
            
        except ValueError:
            logger.error(f"Nível de alerta inválido: {level}")
    
    def _get_channels_for_level(self, level: AlertLevel) -> List[AlertChannel]:
        """Retorna canais configurados para um nível de alerta."""
        channels_config = self.config.alerts.get('channels', [])
        return [AlertChannel(c) for c in channels_config if AlertChannel(c) in self.channels]
    
    async def _process_alert(self, event: AlertEvent):
        """Processa e dispara um alerta."""
        # Verificar cooldown
        if self._is_in_cooldown(event.rule_name):
            logger.debug(f"🔇 Alerta em cooldown: {event.rule_name}")
            return
        
        # Atualizar estatísticas
        self.stats['total_alerts'] += 1
        self.stats['alerts_by_level'][event.level.value] += 1
        self.stats['last_alert_time'] = event.timestamp
        
        # Enviar por cada canal
        for channel in event.channels:
            try:
                await self.channels[channel](event)
                self.stats['alerts_by_channel'][channel.value] += 1
            except Exception as e:
                logger.error(f"💥 Erro ao enviar alerta por {channel.value}: {e}")
        
        # Salvar no histórico
        self.alert_history.append(event)
        
        # Limitar histórico
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-500:]
        
        # Ativar cooldown
        self.cooldown_cache[event.rule_name] = datetime.now()
        
        # Chamar callbacks
        for callback in self.callbacks:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(event.level.value, event.message, event.data)
                else:
                    callback(event.level.value, event.message, event.data)
            except Exception as e:
                logger.error(f"💥 Erro no callback de alerta: {e}")
        
        logger.info(f"🚨 Alerta disparado: {event.level.value.upper()} - {event.message}")
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Verifica se uma regra está em cooldown."""
        if rule_name not in self.cooldown_cache:
            return False
        
        # Encontrar regra para obter cooldown
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False
        
        last_triggered = self.cooldown_cache[rule_name]
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() - last_triggered < cooldown_period
    
    # Canais de envio
    
    async def _send_log(self, event: AlertEvent):
        """Envia alerta por logging."""
        level_map = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.CRITICAL: logging.CRITICAL,
            AlertLevel.EMERGENCY: logging.CRITICAL
        }
        
        logger.log(level_map[event.level], f"ALERTA {event.level.value.upper()}: {event.message}")
    
    async def _send_console(self, event: AlertEvent):
        """Envia alerta para console."""
        emoji = {
            AlertLevel.INFO: "🔵",
            AlertLevel.WARNING: "🟡",
            AlertLevel.CRITICAL: "🔴",
            AlertLevel.EMERGENCY: "🚨"
        }
        
        print(f"\n{emoji[event.level]} [{event.timestamp.strftime('%H:%M:%S')}] {event.level.value.upper()}: {event.message}")
        if event.data:
            print(f"   Dados: {event.data}")
    
    async def _send_file(self, event: AlertEvent):
        """Envia alerta para arquivo."""
        alerts_file = self.config.project_root / "alerts.log"
        
        alert_data = {
            'timestamp': event.timestamp.isoformat(),
            'level': event.level.value,
            'message': event.message,
            'rule': event.rule_name,
            'data': event.data
        }
        
        try:
            with open(alerts_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"💥 Erro ao salvar alerta no arquivo: {e}")
    
    async def _send_email(self, event: AlertEvent):
        """Envia alerta por email."""
        if not self.config.alerts.get('email_config'):
            logger.warning("⚠️  Configuração de email não encontrada")
            return
        
        try:
            email_config = self.config.alerts['email_config']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"[ALERTA {event.level.value.upper()}] {event.message[:50]}"
            
            body = f"""
Alerta {event.level.value.upper()}

Mensagem: {event.message}
Timestamp: {event.timestamp}
Regra: {event.rule_name}
Dados: {json.dumps(event.data, indent=2)}

---
Sistema de Alertas Automáticos
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"📧 Alerta enviado por email: {event.message}")
            
        except Exception as e:
            logger.error(f"💥 Erro ao enviar email: {e}")
    
    async def _send_webhook(self, event: AlertEvent):
        """Envia alerta por webhook."""
        webhook_url = self.config.alerts.get('webhook_url')
        if not webhook_url:
            return
        
        try:
            import aiohttp
            
            payload = {
                'level': event.level.value,
                'message': event.message,
                'timestamp': event.timestamp.isoformat(),
                'rule': event.rule_name,
                'data': event.data
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"🔗 Alerta enviado por webhook: {event.message}")
                    else:
                        logger.warning(f"⚠️  Webhook retornou status {response.status}")
                        
        except Exception as e:
            logger.error(f"💥 Erro ao enviar webhook: {e}")
    
    def check_rules(self, event_type: str, data: Dict) -> List[AlertEvent]:
        """Verifica regras e gera alertas se necessário."""
        triggered_alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._should_trigger_rule(rule, event_type, data):
                channels = rule.channels or self._get_channels_for_level(rule.level)
                
                event = AlertEvent(
                    level=rule.level,
                    message=f"Regra disparada: {rule.name}",
                    timestamp=datetime.now(),
                    data=data,
                    rule_name=rule.name,
                    channels=channels
                )
                
                triggered_alerts.append(event)
        
        return triggered_alerts
    
    def _should_trigger_rule(self, rule: AlertRule, event_type: str, data: Dict) -> bool:
        """Verifica se uma regra deve ser disparada."""
        conditions = rule.conditions
        
        if conditions.get('type') != event_type:
            return False
        
        # Verificar condições específicas
        if event_type == 'new_errors':
            threshold = conditions.get('threshold', 1)
            return data.get('count', 0) >= threshold
        
        elif event_type == 'build_failure':
            consecutive = conditions.get('consecutive', 1)
            return data.get('consecutive_failures', 0) >= consecutive
        
        elif event_type == 'memory_usage':
            threshold = conditions.get('threshold_mb', 100)
            return data.get('usage_mb', 0) <= threshold
        
        elif event_type == 'github_connectivity':
            consecutive = conditions.get('consecutive_failures', 3)
            return data.get('consecutive_failures', 0) >= consecutive
        
        elif event_type == 'error_trend':
            direction = conditions.get('direction', 'increasing')
            threshold = conditions.get('threshold', 10)
            current_trend = data.get('trend', 0)
            
            if direction == 'increasing':
                return current_trend >= threshold
            else:
                return current_trend <= -threshold
        
        return False
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de alertas."""
        return {
            **self.stats,
            'active_rules': len([r for r in self.rules if r.enabled]),
            'total_rules': len(self.rules),
            'cooldown_rules': len(self.cooldown_cache),
            'recent_alerts': [
                {
                    'level': a.level.value,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat(),
                    'rule': a.rule_name
                }
                for a in self.alert_history[-10:]
            ]
        }
    
    def print_stats(self):
        """Imprime estatísticas de alertas."""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("🚨 ALERT SYSTEM STATS")
        print("="*60)
        print(f"Total Alerts: {stats['total_alerts']}")
        print(f"Active Rules: {stats['active_rules']}/{stats['total_rules']}")
        print(f"Cooldown Rules: {stats['cooldown_rules']}")
        
        print("\n📊 ALERTS BY LEVEL:")
        for level, count in stats['alerts_by_level'].items():
            print(f"  {level}: {count}")
        
        print("\n📡 ALERTS BY CHANNEL:")
        for channel, count in stats['alerts_by_channel'].items():
            print(f"  {channel}: {count}")
        
        if stats['recent_alerts']:
            print("\n📋 RECENT ALERTS:")
            for alert in stats['recent_alerts']:
                print(f"  {alert['level'].upper()}: {alert['message'][:50]}")
        
        print("="*60)
    
    def export_alerts(self, days: int = 7) -> Path:
        """Exporta alertas para arquivo JSON."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff
        ]
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'period_days': days,
            'total_alerts': len(recent_alerts),
            'alerts': [
                {
                    'level': a.level.value,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat(),
                    'rule': a.rule_name,
                    'channels': [c.value for c in a.channels],
                    'data': a.data
                }
                for a in recent_alerts
            ],
            'stats': self.get_stats()
        }
        
        export_file = self.config.project_root / f"alerts-export-{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📤 Alertas exportados: {export_file}")
            return export_file
            
        except Exception as e:
            logger.error(f"💥 Erro ao exportar alertas: {e}")
            return export_file


def main():
    """Função principal para teste."""
    alert_system = AlertSystem()
    
    # Testar alerta manual
    asyncio.run(alert_system.trigger_alert(
        "warning",
        "Teste de alerta manual",
        {"test": True}
    ))
    
    # Imprimir estatísticas
    alert_system.print_stats()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())