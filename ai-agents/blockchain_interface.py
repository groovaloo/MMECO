#!/usr/bin/env python3
"""
Blockchain Interface - Moral Money Ecosystem
============================================

Interface que conecta o Batch Processor ao Substrate node.
Transforma eventos em transações Substrate e envia para a blockchain.

Características:
- Conexão WebSocket com Substrate node
- Mapeamento de eventos para chamadas pallet
- Batch transactions para eficiência
- Error handling e retry logic
- Integração com batch_processor.py
"""

import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Importa Substrate interface
try:
    from substrateinterface import SubstrateInterface, Keypair, ExtrinsicReceipt
    from substrateinterface.exceptions import SubstrateRequestException, ConfigurationError
    SUBSTRATE_AVAILABLE = True
except ImportError:
    SUBSTRATE_AVAILABLE = False
    logging.warning("⚠️  Substrate interface não disponível. Instale com: pip install substrate-interface")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    REPUTATION = "reputation"
    PROOF = "proof"
    BUILD_COIN = "build_coin"
    PROJECT = "project"

@dataclass
class BlockchainConfig:
    """Configuração da conexão blockchain"""
    ws_url: str = "ws://localhost:9944"
    ss58_format: int = 42
    type_registry_preset: str = "default"
    retry_attempts: int = 3
    retry_delay: float = 2.0

class BlockchainInterface:
    """Interface para comunicação com Substrate node"""
    
    def __init__(self, config: BlockchainConfig = None):
        self.config = config or BlockchainConfig()
        self.substrate = None
        self.keypair = None
        
        if not SUBSTRATE_AVAILABLE:
            logger.error("❌ Substrate interface não disponível")
            raise ImportError("Substrate interface não instalada")
        
        self.connect()
    
    def connect(self):
        """Conecta ao Substrate node"""
        try:
            self.substrate = SubstrateInterface(
                url=self.config.ws_url,
                ss58_format=self.config.ss58_format,
                type_registry_preset=self.config.type_registry_preset
            )
            
            # Cria keypair para assinatura (em produção usaria uma wallet real)
            self.keypair = Keypair.create_from_uri("//Alice")
            
            logger.info(f"✅ Conectado ao Substrate node: {self.config.ws_url}")
            
        except Exception as e:
            logger.error(f"❌ Falha na conexão Substrate: {e}")
            raise
    
    def map_event_to_call(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mapeia evento para chamada Substrate"""
        try:
            event_type = event.get('event_type')
            data = event.get('data', {})
            agent_id = event.get('agent_id', '')
            
            if event_type == EventType.REPUTATION.value:
                return self._map_reputation_call(event, data, agent_id)
            elif event_type == EventType.PROOF.value:
                return self._map_proof_call(event, data, agent_id)
            elif event_type == EventType.BUILD_COIN.value:
                return self._map_buildcoin_call(event, data, agent_id)
            elif event_type == EventType.PROJECT.value:
                return self._map_project_call(event, data, agent_id)
            
            logger.warning(f"⚠️  Tipo de evento desconhecido: {event_type}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Falha ao mapear evento: {e}")
            return None
    
    def _map_reputation_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia reputação para submit_reputation"""
        return {
            'call_module': 'Reputation',
            'call_function': 'submit_reputation',
            'call_params': {
                'agent_id': agent_id,
                'reputation_score': data.get('score', 0),
                'reputation_type': data.get('type', 'general'),
                'metadata': data.get('metadata', {}),
                'timestamp': event.get('timestamp', time.time())
            }
        }
    
    def _map_proof_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia proof para submit_proof"""
        return {
            'call_module': 'Reputation',
            'call_function': 'submit_proof',
            'call_params': {
                'agent_id': agent_id,
                'proof_type': data.get('type', 'unknown'),
                'proof_data': data.get('data', {}),
                'proof_hash': data.get('hash', ''),
                'timestamp': event.get('timestamp', time.time())
            }
        }
    
    def _map_buildcoin_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia buildcoin para mint_buildcoin"""
        return {
            'call_module': 'Reputation',
            'call_function': 'mint_buildcoin',
            'call_params': {
                'agent_id': agent_id,
                'amount': data.get('amount', 0),
                'reason': data.get('reason', 'unknown'),
                'metadata': data.get('metadata', {}),
                'timestamp': event.get('timestamp', time.time())
            }
        }
    
    def _map_project_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia project para submit_project"""
        return {
            'call_module': 'Reputation',
            'call_function': 'submit_project',
            'call_params': {
                'agent_id': agent_id,
                'project_id': data.get('project_id', ''),
                'project_data': data.get('data', {}),
                'project_type': data.get('type', 'unknown'),
                'timestamp': event.get('timestamp', time.time())
            }
        }
    
    def build_batch_transaction(self, events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Constrói transação batch para múltiplos eventos"""
        try:
            calls = []
            
            for event in events:
                call = self.map_event_to_call(event)
                if call:
                    calls.append(call)
            
            if not calls:
                return None
            
            # Cria batch call
            batch_call = {
                'call_module': 'Utility',
                'call_function': 'batch',
                'call_params': {
                    'calls': calls
                }
            }
            
            return batch_call
            
        except Exception as e:
            logger.error(f"❌ Falha ao construir batch: {e}")
            return None
    
    def send_transaction(self, batch_call: Dict[str, Any]) -> Dict[str, Any]:
        """Envia transação para o blockchain"""
        try:
            # Constrói a extrinsic
            extrinsic = self.substrate.create_signed_extrinsic(
                call=self.substrate.compose_call(**batch_call),
                keypair=self.keypair
            )
            
            # Envia a transação
            receipt = self.substrate.submit_extrinsic(
                extrinsic,
                wait_for_inclusion=True,
                wait_for_finalization=True
            )
            
            result = {
                'success': True,
                'block_hash': receipt.block_hash,
                'extrinsic_hash': receipt.extrinsic_hash,
                'events': receipt.triggered_events,
                'fee': receipt.total_fee_amount
            }
            
            logger.info(f"✅ Transação enviada com sucesso: {receipt.extrinsic_hash}")
            return result
            
        except SubstrateRequestException as e:
            logger.error(f"❌ Erro na requisição Substrate: {e}")
            return {'success': False, 'error': str(e), 'type': 'substrate_request'}
        except Exception as e:
            logger.error(f"❌ Erro ao enviar transação: {e}")
            return {'success': False, 'error': str(e), 'type': 'general'}
    
    def send_batch_with_retry(self, batch_call: Dict[str, Any]) -> Dict[str, Any]:
        """Envia batch com retry logic"""
        for attempt in range(self.config.retry_attempts):
            try:
                result = self.send_transaction(batch_call)
                
                if result['success']:
                    return result
                
                logger.warning(f"⚠️  Tentativa {attempt + 1} falhou: {result.get('error')}")
                
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"❌ Falha na tentativa {attempt + 1}: {e}")
                
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
        
        return {'success': False, 'error': 'Todas as tentativas falharam', 'type': 'retry_exhausted'}
    
    def process_batch(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Processa batch de eventos para blockchain"""
        try:
            batch_type = batch.get('type', 'unknown')
            events = batch.get('events', [])
            
            logger.info(f"📤 Processando batch para blockchain: {batch_type} ({len(events)} eventos)")
            
            if not events:
                return {'success': True, 'message': 'Batch vazio'}
            
            # Constrói transação batch
            batch_call = self.build_batch_transaction(events)
            
            if not batch_call:
                return {'success': False, 'error': 'Nenhuma chamada válida gerada'}
            
            # Envia com retry
            result = self.send_batch_with_retry(batch_call)
            
            if result['success']:
                logger.info(f"✅ Batch processado com sucesso: {batch_type}")
            else:
                logger.error(f"❌ Falha no processamento do batch: {batch_type} - {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento do batch: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde da conexão blockchain"""
        try:
            if not self.substrate:
                return {'status': 'disconnected', 'error': 'Sem conexão Substrate'}
            
            # Testa conexão
            self.substrate.get_block_hash()
            
            return {
                'status': 'connected',
                'ws_url': self.config.ws_url,
                'ss58_format': self.config.ss58_format,
                'retry_attempts': self.config.retry_attempts
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'ws_url': self.config.ws_url
            }

def send_to_blockchain(batch: Dict[str, Any], config: BlockchainConfig = None) -> bool:
    """Interface pública para envio ao blockchain (substitui mock)"""
    try:
        # Cria interface blockchain
        blockchain = BlockchainInterface(config)
        
        # Processa batch
        result = blockchain.process_batch(batch)
        
        return result['success']
        
    except Exception as e:
        logger.error(f"❌ Falha na interface blockchain: {e}")
        return False

def main():
    """Teste da Blockchain Interface"""
    
    print("🔗 TESTE DA BLOCKCHAIN INTERFACE")
    print("="*50)
    
    try:
        # Cria interface blockchain
        blockchain = BlockchainInterface()
        
        # Verifica saúde
        health = blockchain.health_check()
        print(f"Saúde da conexão: {'✅' if health['status'] == 'connected' else '❌'}")
        
        if health['status'] != 'connected':
            print(f"❌ Erro: {health.get('error', 'Desconhecido')}")
            return
        
        print(f"Conectado ao: {health['ws_url']}")
        print()
        
        # Testa processamento de batch
        print("🧪 TESTE DE PROCESSAMENTO")
        print("-"*30)
        
        # Cria batch de teste
        test_batch = {
            'type': 'reputation',
            'events': [
                {
                    'event_id': 'test_001',
                    'event_type': 'reputation',
                    'timestamp': time.time(),
                    'agent_id': 'test_agent',
                    'priority': 1,
                    'data': {
                        'score': 100,
                        'type': 'community',
                        'metadata': {'source': 'test'}
                    }
                }
            ],
            'timestamp': time.time()
        }
        
        success = blockchain.process_batch(test_batch)
        print(f"Processamento: {'✅' if success['success'] else '❌'}")
        
        if not success['success']:
            print(f"Erro: {success.get('error', 'Desconhecido')}")
        
        print()
        print("✅ TESTE DA BLOCKCHAIN INTERFACE CONCLUÍDO")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    main()