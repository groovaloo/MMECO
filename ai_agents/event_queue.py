#!/usr/bin/env python3
"""
Event Queue - Moral Money Ecosystem
===================================

Sistema de filas de eventos baseado em Redis Streams.
Buffer central para eventos dos agentes antes do processamento em lote.

Características:
- Redis Streams para armazenamento e ordenação
- TTL de 24 horas para eventos
- Sharding por tipo de evento
- Pub/Sub para distribuição
- Alta performance para 100 agentes
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
    priority: int = 0  # 0-10, maior = mais prioritário

class EventQueue:
    """Sistema de filas de eventos baseado em Redis Streams"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self.streams = {
            EventType.REPUTATION: "events:reputation",
            EventType.PROOF: "events:proof",
            EventType.BUILD_COIN: "events:build_coin",
            EventType.PROJECT: "events:project"
        }
        
        # Configurações
        self.ttl_hours = 24  # TTL de 24 horas
        self.max_length = 10000  # Máximo de eventos por stream
        
        self.connect()
        self.setup_streams()
    
    def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("✅ Conexão com Redis estabelecida")
        except Exception as e:
            logger.error(f"❌ Falha na conexão com Redis: {e}")
            raise
    
    def setup_streams(self):
        """Configura os streams no Redis"""
        try:
            for stream_name in self.streams.values():
                # Cria stream se não existir (Redis cria automaticamente)
                # Configura TTL
                self.redis_client.expire(stream_name, self.ttl_hours * 3600)
            
            logger.info("✅ Streams configurados")
        except Exception as e:
            logger.error(f"❌ Falha na configuração dos streams: {e}")
    
    def publish_event(self, event: Event) -> bool:
        """Publica evento no stream apropriado"""
        try:
            stream_name = self.streams[event.event_type]
            
            # Converte evento para JSON
            event_data = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': str(event.timestamp),  # Converte para string
                'agent_id': event.agent_id,
                'data': json.dumps(event.data),  # Converte dict para string JSON
                'priority': str(event.priority)  # Converte para string
            }
            
            # Publica no stream
            message_id = self.redis_client.xadd(
                stream_name,
                event_data,
                maxlen=self.max_length,
                approximate=True
            )
            
            # Configura TTL
            self.redis_client.expire(stream_name, self.ttl_hours * 3600)
            
            logger.debug(f"📨 Evento publicado: {event.event_type.value} - {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha ao publicar evento: {e}")
            return False
    
    def consume_events(self, event_type: EventType, count: int = 100) -> List[Dict[str, Any]]:
        """Consome eventos de um stream"""
        try:
            stream_name = self.streams[event_type]
            
            # Lê eventos do stream
            messages = self.redis_client.xread(
                {stream_name: '0'},  # Começa do início
                count=count,
                block=1000  # Espera 1 segundo por novos eventos
            )
            
            events = []
            if messages:
                for stream, msg_list in messages:
                    for message_id, fields in msg_list:
                        # Converte campos de volta para Python objects
                        event_data = {
                            'message_id': message_id.decode(),
                            'event_id': fields[b'event_id'].decode(),
                            'event_type': fields[b'event_type'].decode(),
                            'timestamp': float(fields[b'timestamp']),
                            'agent_id': fields[b'agent_id'].decode(),
                            'priority': int(fields[b'priority']),
                            'data': json.loads(fields[b'data'].decode())
                        }
                        events.append(event_data)
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Falha ao consumir eventos: {e}")
            return []
    
    def get_stream_length(self, event_type: EventType) -> int:
        """Obtém o número de eventos em um stream"""
        try:
            stream_name = self.streams[event_type]
            length = self.redis_client.xlen(stream_name)
            return length
        except Exception as e:
            logger.error(f"❌ Falha ao obter tamanho do stream: {e}")
            return 0
    
    def get_all_streams_length(self) -> Dict[str, int]:
        """Obtém o tamanho de todos os streams"""
        lengths = {}
        for event_type in EventType:
            lengths[event_type.value] = self.get_stream_length(event_type)
        return lengths
    
    def delete_old_events(self, max_age_hours: int = 24):
        """Remove eventos antigos (backup do TTL)"""
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            
            for event_type in EventType:
                stream_name = self.streams[event_type]
                
                # Remove eventos antigos
                self.redis_client.xtrim(
                    stream_name,
                    maxlen=self.max_length,
                    approximate=True
                )
            
            logger.info("✅ Eventos antigos removidos")
            
        except Exception as e:
            logger.error(f"❌ Falha ao remover eventos antigos: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de filas"""
        try:
            # Verifica conexão
            self.redis_client.ping()
            
            # Obtém estatísticas
            stream_lengths = self.get_all_streams_length()
            total_events = sum(stream_lengths.values())
            
            return {
                'status': 'healthy',
                'redis_connected': True,
                'streams': stream_lengths,
                'total_events': total_events,
                'max_length': self.max_length,
                'ttl_hours': self.ttl_hours
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'redis_connected': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Limpeza do sistema"""
        try:
            # Remove streams antigos
            for stream_name in self.streams.values():
                self.redis_client.delete(stream_name)
            
            logger.info("✅ Limpeza do sistema de filas concluída")
            
        except Exception as e:
            logger.error(f"❌ Falha na limpeza: {e}")

def main():
    """Teste do Event Queue"""
    
    print("📨 TESTE DO EVENT QUEUE")
    print("="*50)
    
    # Cria fila de eventos
    event_queue = EventQueue()
    
    # Verifica saúde
    health = event_queue.health_check()
    print(f"Saúde do sistema: {'✅' if health['status'] == 'healthy' else '❌'}")
    
    if not health['redis_connected']:
        print("❌ Redis não está disponível")
        print("   Certifique-se de que o Redis está rodando em localhost:6379")
        return
    
    print(f"Eventos nos streams: {health['total_events']}")
    print()
    
    # Cria eventos de teste
    print("📝 CRIANDO EVENTOS DE TESTE")
    print("-"*30)
    
    test_events = [
        Event(
            event_id="test_001",
            event_type=EventType.REPUTATION,
            timestamp=time.time(),
            agent_id="Nuno",
            data={
                'domain': 'Construction',
                'amount': 100,
                'description': '8h de trabalho'
            },
            priority=5
        ),
        Event(
            event_id="test_002",
            event_type=EventType.PROOF,
            timestamp=time.time(),
            agent_id="Maria",
            data={
                'proof_type': 'Photo',
                'description': 'Foto da obra concluída'
            },
            priority=8
        ),
        Event(
            event_id="test_003",
            event_type=EventType.BUILD_COIN,
            timestamp=time.time(),
            agent_id="Cooperativa",
            data={
                'amount': 1000,
                'reason': 'Projeto aprovado'
            },
            priority=10
        )
    ]
    
    # Publica eventos
    for event in test_events:
        success = event_queue.publish_event(event)
        print(f"Evento {event.event_id}: {'✅' if success else '❌'}")
    
    print()
    
    # Consome eventos
    print("📨 CONSUMINDO EVENTOS")
    print("-"*20)
    
    for event_type in EventType:
        events = event_queue.consume_events(event_type, count=10)
        print(f"{event_type.value}: {len(events)} eventos")
        for event in events:
            print(f"  - {event['event_id']} ({event['agent_id']})")
    
    print()
    
    # Verifica estatísticas finais
    final_health = event_queue.health_check()
    print("📊 ESTATÍSTICAS FINAIS")
    print("-"*20)
    print(f"Eventos totais: {final_health['total_events']}")
    for stream, length in final_health['streams'].items():
        print(f"  {stream}: {length}")
    
    print()
    print("✅ TESTE DO EVENT QUEUE CONCLUÍDO")

if __name__ == "__main__":
    main()
