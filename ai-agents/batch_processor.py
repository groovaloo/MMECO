#!/usr/bin/env python3
"""
Batch Processor - Moral Money Ecosystem
=======================================

Processador de lotes que lê eventos do Redis, agrupa em batches
e prepara para o blockchain interface.

Características:
- Batch trigger: 50 eventos OU 2 minutos
- Cooldown verification usando Redis
- Pending events armazenados no Redis
- Mock blockchain interface para testes
- Integração com event_queue.py
"""

import json
import logging
import time
import redis
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    REPUTATION = "reputation"
    PROOF = "proof"
    BUILD_COIN = "build_coin"
    PROJECT = "project"

@dataclass
class Event:
    """Evento do sistema"""
    event_id: str
    event_type: EventType
    timestamp: float
    agent_id: str
    data: Dict[str, Any]
    priority: int = 0

def send_to_blockchain(batch: Dict[str, Any]):
    """Mock do envio para blockchain interface"""
    try:
        logger.info(f"📤 Enviando batch para blockchain: {batch['type']} ({len(batch['events'])} eventos)")
        
        # Simula processamento
        time.sleep(0.1)
        
        # Simula sucesso/fracasso aleatório para testes
        import random
        if random.random() < 0.1:  # 10% de falhas
            raise Exception("Simulação de falha de blockchain")
        
        logger.info(f"✅ Batch processado com sucesso: {batch['type']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Falha no mock do blockchain: {e}")
        return False

class BatchProcessor:
    """Processador de lotes com cooldown verification"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        
        # Configurações
        self.batch_size = 50
        self.batch_timeout = 120  # 2 minutos
        self.cooldown_minutes = 15
        
        # Streams do Event Queue
        self.streams = {
            EventType.REPUTATION: "events:reputation",
            EventType.PROOF: "events:proof",
            EventType.BUILD_COIN: "events:build_coin",
            EventType.PROJECT: "events:project"
        }
        
        # Redis keys
        self.cooldown_prefix = "cooldown:"
        self.pending_stream = "pending_events"
        
        self.connect()
    
    def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("✅ Batch Processor conectado ao Redis")
        except Exception as e:
            logger.error(f"❌ Falha na conexão do Batch Processor: {e}")
            raise
    
    def check_cooldown(self, agent_id: str) -> bool:
        """Verifica se agente está em cooldown (15 minutos)"""
        try:
            cooldown_key = f"{self.cooldown_prefix}{agent_id}"
            last_rep = self.redis_client.get(cooldown_key)
            
            now = time.time()
            
            if last_rep:
                last_time = float(last_rep)
                
                if now - last_time < (self.cooldown_minutes * 60):
                    return False  # Em cooldown
            
            # Atualiza timestamp do último recebimento
            self.redis_client.setex(
                cooldown_key,
                self.cooldown_minutes * 60 * 2,  # TTL: 30 minutos
                now
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha ao verificar cooldown: {e}")
            return False
    
    def store_pending_event(self, event: Dict[str, Any]):
        """Armazena evento pendente no Redis"""
        try:
            # Converte campos para string para o Redis
            event_str = {
                'event_id': str(event.get('event_id', '')),
                'event_type': str(event.get('event_type', '')),
                'timestamp': str(event.get('timestamp', '')),
                'agent_id': str(event.get('agent_id', '')),
                'priority': str(event.get('priority', 0)),
                'data': json.dumps(event.get('data', {}))
            }
            
            self.redis_client.xadd(
                self.pending_stream,
                event_str,
                maxlen=1000,
                approximate=True
            )
            logger.debug(f"⏳ Evento armazenado como pendente: {event.get('event_id')}")
            
        except Exception as e:
            logger.error(f"❌ Falha ao armazenar evento pendente: {e}")
    
    def process_pending_events(self) -> List[Dict[str, Any]]:
        """Processa eventos pendentes"""
        try:
            # Lê eventos pendentes
            messages = self.redis_client.xread(
                {self.pending_stream: '0'},
                count=100,
                block=1000
            )
            
            pending_events = []
            if messages:
                for stream, msg_list in messages:
                    for message_id, fields in msg_list:
                        event_data = {
                            'message_id': message_id.decode(),
                            'event_id': fields[b'event_id'].decode(),
                            'event_type': fields[b'event_type'].decode(),
                            'timestamp': float(fields[b'timestamp']),
                            'agent_id': fields[b'agent_id'].decode(),
                            'priority': int(fields[b'priority']),
                            'data': json.loads(fields[b'data'].decode())
                        }
                        pending_events.append(event_data)
                        
                        # Remove evento processado
                        self.redis_client.xdel(self.pending_stream, message_id)
            
            return pending_events
            
        except Exception as e:
            logger.error(f"❌ Falha ao processar eventos pendentes: {e}")
            return []
    
    def collect_events(self) -> List[Dict[str, Any]]:
        """Coleta eventos de todos os streams"""
        try:
            all_events = []
            
            # Coleta eventos de streams principais
            for stream_name in self.streams.values():
                messages = self.redis_client.xread(
                    {stream_name: '0'},
                    count=100,
                    block=1000
                )
                
                if messages:
                    for stream, msg_list in messages:
                        for message_id, fields in msg_list:
                            event_data = {
                                'message_id': message_id.decode(),
                                'event_id': fields[b'event_id'].decode(),
                                'event_type': fields[b'event_type'].decode(),
                                'timestamp': float(fields[b'timestamp']),
                                'agent_id': fields[b'agent_id'].decode(),
                                'priority': int(fields[b'priority']),
                                'data': json.loads(fields[b'data'].decode())
                            }
                            all_events.append(event_data)
                            
                            # Remove evento processado
                            self.redis_client.xdel(stream_name, message_id)
            
            # Processa eventos pendentes
            pending_events = self.process_pending_events()
            all_events.extend(pending_events)
            
            return all_events
            
        except Exception as e:
            logger.error(f"❌ Falha ao coletar eventos: {e}")
            return []
    
    def filter_events(self, events: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Filtra eventos por cooldown"""
        ready_events = []
        pending_events = []
        
        for event in events:
            if event['event_type'] == EventType.REPUTATION.value:
                if self.check_cooldown(event['agent_id']):
                    ready_events.append(event)
                else:
                    pending_events.append(event)
            else:
                ready_events.append(event)
        
        # Armazena eventos pendentes
        for event in pending_events:
            self.store_pending_event(event)
        
        return ready_events, pending_events
    
    def group_by_type(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa eventos por tipo"""
        grouped = {}
        for event_type in EventType:
            grouped[event_type.value] = []
        
        for event in events:
            grouped[event['event_type']].append(event)
        
        return grouped
    
    def process_batch(self):
        """Processa um batch de eventos"""
        try:
            # Coleta eventos
            events = self.collect_events()
            
            if not events:
                return False
            
            logger.info(f"📦 Processando batch: {len(events)} eventos")
            
            # Filtra por cooldown
            ready_events, pending_events = self.filter_events(events)
            
            # Agrupa por tipo
            grouped_events = self.group_by_type(ready_events)
            
            # Envia para blockchain mock
            success_count = 0
            for batch_type, batch_events in grouped_events.items():
                if batch_events:  # Só envia se houver eventos
                    batch = {
                        'type': batch_type,
                        'events': batch_events,
                        'timestamp': time.time()
                    }
                    if send_to_blockchain(batch):
                        success_count += 1
            
            logger.info(f"📊 Batch concluído: {success_count}/{len(grouped_events)} tipos processados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha no processamento do batch: {e}")
            return False
    
    def run(self):
        """Loop principal do batch processor"""
        logger.info("🚀 Batch Processor iniciado")
        
        last_batch_time = time.time()
        
        while True:
            try:
                current_time = time.time()
                
                # Verifica triggers do batch
                events_count = self.get_total_events_count()
                time_elapsed = current_time - last_batch_time
                
                should_process = (
                    events_count >= self.batch_size or
                    time_elapsed >= self.batch_timeout
                )
                
                if should_process and events_count > 0:
                    logger.info(f"⏰ Trigger do batch: {events_count} eventos, {time_elapsed:.1f}s")
                    self.process_batch()
                    last_batch_time = current_time
                
                # Dorme um pouco para não sobrecarregar
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Batch Processor interrompido")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                time.sleep(5)
    
    def get_total_events_count(self) -> int:
        """Obtém contagem total de eventos"""
        try:
            total = 0
            
            # Conta eventos nos streams principais
            for stream_name in self.streams.values():
                total += self.redis_client.xlen(stream_name)
            
            # Conta eventos pendentes
            total += self.redis_client.xlen(self.pending_stream)
            
            return total
            
        except Exception as e:
            logger.error(f"❌ Falha ao obter contagem de eventos: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do batch processor"""
        try:
            self.redis_client.ping()
            
            return {
                'status': 'healthy',
                'redis_connected': True,
                'total_events': self.get_total_events_count(),
                'batch_size': self.batch_size,
                'batch_timeout': self.batch_timeout,
                'cooldown_minutes': self.cooldown_minutes
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'redis_connected': False,
                'error': str(e)
            }

def main():
    """Teste do Batch Processor"""
    
    print("📦 TESTE DO BATCH PROCESSOR")
    print("="*50)
    
    # Cria batch processor
    batch_processor = BatchProcessor()
    
    # Verifica saúde
    health = batch_processor.health_check()
    print(f"Saúde do sistema: {'✅' if health['status'] == 'healthy' else '❌'}")
    
    if not health['redis_connected']:
        print("❌ Redis não está disponível")
        return
    
    print(f"Eventos no sistema: {health['total_events']}")
    print()
    
    # Testa processamento de batch
    print("🧪 TESTE DE PROCESSAMENTO")
    print("-"*30)
    
    success = batch_processor.process_batch()
    print(f"Processamento: {'✅' if success else '❌'}")
    
    print()
    print("✅ TESTE DO BATCH PROCESSOR CONCLUÍDO")

if __name__ == "__main__":
    main()