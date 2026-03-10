#!/usr/bin/env python3
"""
Sistema P2P Offline para Moral Money

Implementa a rede peer-to-peer offline para comunicação entre nós
sem dependência de internet. Baseado em tecnologias de mesh networking
e sincronização de blockchain em ambientes offline.

Funcionalidades:
- Descoberta de nós na rede local
- Sincronização de blockchain offline
- Comunicação segura entre pares
- Resiliência a falhas de conexão
"""

import socket
import threading
import json
import hashlib
import time
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from cryptography.fernet import Fernet
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeType(Enum):
    FULL_NODE = "FullNode"
    LIGHT_NODE = "LightNode"
    MOBILE_NODE = "MobileNode"

class ConnectionState(Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    SYNCING = "Syncing"
    ERROR = "Error"

@dataclass
class NodeInfo:
    node_id: str
    ip_address: str
    port: int
    node_type: NodeType
    last_seen: float
    blockchain_height: int
    capabilities: List[str]

@dataclass
class BlockData:
    block_hash: str
    block_number: int
    timestamp: float
    transactions: List[Dict]
    previous_hash: str

@dataclass
class TransactionData:
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    timestamp: float
    signature: str

class P2POffline:
    """
    Sistema P2P Offline para Moral Money
    
    Características:
    - Operação totalmente offline
    - Descoberta automática de nós
    - Sincronização eficiente de blockchain
    - Comunicação segura e criptografada
    - Resiliência a falhas de rede
    """
    
    def __init__(self, node_id: str, port: int = 8080, node_type: NodeType = NodeType.FULL_NODE):
        self.node_id = node_id
        self.port = port
        self.node_type = node_type
        self.ip_address = self.get_local_ip()
        
        # Estruturas de dados
        self.peers: Dict[str, NodeInfo] = {}
        self.blockchain_data: Dict[int, BlockData] = {}
        self.transaction_pool: List[TransactionData] = []
        self.connections: Dict[str, socket.socket] = {}
        
        # Configurações de segurança
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Threads de operação
        self.discovery_thread = None
        self.sync_thread = None
        self.server_thread = None
        
        # Estado
        self.is_running = False
        self.blockchain_height = 0
        
        logger.info(f"Nó P2P iniciado: {self.node_id} em {self.ip_address}:{self.port}")
    
    def get_local_ip(self) -> str:
        """Obtém o IP local da máquina"""
        try:
            # Cria um socket temporário para descobrir o IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def start_network(self):
        """Inicia a rede P2P offline"""
        self.is_running = True
        
        # Inicia threads de operação
        self.discovery_thread = threading.Thread(target=self.discovery_loop, daemon=True)
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.server_thread = threading.Thread(target=self.server_loop, daemon=True)
        
        self.discovery_thread.start()
        self.sync_thread.start()
        self.server_thread.start()
        
        logger.info("Rede P2P offline iniciada")
    
    def stop_network(self):
        """Para a rede P2P offline"""
        self.is_running = False
        
        # Fecha conexões
        for conn in self.connections.values():
            try:
                conn.close()
            except:
                pass
        
        self.connections.clear()
        logger.info("Rede P2P offline encerrada")
    
    def discovery_loop(self):
        """Loop de descoberta de nós na rede local"""
        discovery_port = 9090
        
        # Socket para descoberta
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        discovery_socket.bind(('', discovery_port))
        
        # Envia anúncios de descoberta
        def send_discovery():
            while self.is_running:
                try:
                    message = {
                        "type": "discovery",
                        "node_id": self.node_id,
                        "ip_address": self.ip_address,
                        "port": self.port,
                        "node_type": self.node_type.value,
                        "height": self.blockchain_height,
                        "timestamp": time.time()
                    }
                    
                    # Envia broadcast
                    data = json.dumps(message).encode()
                    discovery_socket.sendto(data, ('<broadcast>', discovery_port))
                    
                except Exception as e:
                    logger.error(f"Erro no envio de descoberta: {e}")
                
                time.sleep(10)  # Envia a cada 10 segundos
        
        # Recebe respostas de descoberta
        def receive_discovery():
            while self.is_running:
                try:
                    data, addr = discovery_socket.recvfrom(1024)
                    message = json.loads(data.decode())
                    
                    if message.get("type") == "discovery" and message.get("node_id") != self.node_id:
                        self.add_peer(message)
                        
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Erro no recebimento de descoberta: {e}")
        
        # Inicia threads de descoberta
        threading.Thread(target=send_discovery, daemon=True).start()
        threading.Thread(target=receive_discovery, daemon=True).start()
    
    def add_peer(self, peer_info: Dict):
        """Adiciona um peer à lista de conhecidos"""
        node_id = peer_info["node_id"]
        
        if node_id not in self.peers:
            peer = NodeInfo(
                node_id=node_id,
                ip_address=peer_info["ip_address"],
                port=peer_info["port"],
                node_type=NodeType(peer_info["node_type"]),
                last_seen=time.time(),
                blockchain_height=peer_info["height"],
                capabilities=["blockchain_sync", "transaction_propagation"]
            )
            
            self.peers[node_id] = peer
            logger.info(f"Novo peer descoberto: {node_id} em {peer.ip_address}:{peer.port}")
            
            # Conecta ao peer
            self.connect_to_peer(peer)
    
    def connect_to_peer(self, peer: NodeInfo):
        """Conecta a um peer"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((peer.ip_address, peer.port))
            
            self.connections[peer.node_id] = sock
            
            # Envia handshake
            handshake = {
                "type": "handshake",
                "node_id": self.node_id,
                "capabilities": ["blockchain_sync", "transaction_propagation"]
            }
            
            self.send_message(sock, handshake)
            
            # Inicia thread de escuta
            threading.Thread(target=self.listen_to_peer, args=(peer.node_id, sock), daemon=True).start()
            
            logger.info(f"Conectado ao peer: {peer.node_id}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao peer {peer.node_id}: {e}")
    
    def listen_to_peer(self, peer_id: str, sock: socket.socket):
        """Escuta mensagens de um peer"""
        while self.is_running and peer_id in self.connections:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                
                message = self.decrypt_message(data)
                self.handle_message(peer_id, message)
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Erro ao escutar peer {peer_id}: {e}")
                break
        
        # Remove peer desconectado
        if peer_id in self.connections:
            del self.connections[peer_id]
        if peer_id in self.peers:
            del self.peers[peer_id]
    
    def server_loop(self):
        """Loop do servidor P2P"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.ip_address, self.port))
        server_socket.listen(5)
        
        logger.info(f"Servidor P2P escutando em {self.ip_address}:{self.port}")
        
        while self.is_running:
            try:
                client_socket, addr = server_socket.accept()
                logger.info(f"Conexão recebida de {addr}")
                
                # Inicia thread para tratar a conexão
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Erro no servidor P2P: {e}")
    
    def handle_client(self, client_socket: socket.socket):
        """Trata conexão de cliente"""
        try:
            data = client_socket.recv(4096)
            message = self.decrypt_message(data)
            
            if message.get("type") == "handshake":
                # Responde ao handshake
                response = {
                    "type": "handshake_response",
                    "node_id": self.node_id,
                    "status": "accepted"
                }
                self.send_message(client_socket, response)
                
            elif message.get("type") == "sync_request":
                # Envia dados de sincronização
                self.handle_sync_request(client_socket, message)
                
        except Exception as e:
            logger.error(f"Erro ao tratar cliente: {e}")
        finally:
            client_socket.close()
    
    def handle_message(self, peer_id: str, message: Dict):
        """Trata mensagens recebidas de peers"""
        msg_type = message.get("type")
        
        if msg_type == "sync_request":
            self.handle_sync_request(self.connections[peer_id], message)
        elif msg_type == "block_data":
            self.handle_block_data(message)
        elif msg_type == "transaction":
            self.handle_transaction(message)
        elif msg_type == "sync_complete":
            logger.info(f"Sincronização concluída com {peer_id}")
    
    def handle_sync_request(self, sock: socket.socket, message: Dict):
        """Trata solicitação de sincronização"""
        start_height = message.get("start_height", 0)
        end_height = message.get("end_height", self.blockchain_height)
        
        # Envia blocos solicitados
        for height in range(start_height, min(end_height + 1, self.blockchain_height + 1)):
            if height in self.blockchain_data:
                block = self.blockchain_data[height]
                response = {
                    "type": "block_data",
                    "block": asdict(block)
                }
                self.send_message(sock, response)
        
        # Indica fim da sincronização
        self.send_message(sock, {"type": "sync_complete"})
    
    def handle_block_data(self, message: Dict):
        """Trata dados de bloco recebidos"""
        block_data = message["block"]
        block = BlockData(**block_data)
        
        if block.block_number not in self.blockchain_data:
            self.blockchain_data[block.block_number] = block
            self.blockchain_height = max(self.blockchain_height, block.block_number)
            
            logger.info(f"Bloco recebido: {block.block_number}")
    
    def handle_transaction(self, message: Dict):
        """Trata transação recebida"""
        tx_data = message["transaction"]
        tx = TransactionData(**tx_data)
        
        if tx not in self.transaction_pool:
            self.transaction_pool.append(tx)
            logger.info(f"Transação recebida: {tx.tx_hash}")
    
    def sync_loop(self):
        """Loop de sincronização com peers"""
        while self.is_running:
            try:
                for peer_id, peer in self.peers.items():
                    if peer.blockchain_height > self.blockchain_height:
                        self.request_sync(peer)
                
                time.sleep(30)  # Sincroniza a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no loop de sincronização: {e}")
    
    def request_sync(self, peer: NodeInfo):
        """Solicita sincronização a um peer"""
        if peer.node_id not in self.connections:
            return
        
        sock = self.connections[peer.node_id]
        
        request = {
            "type": "sync_request",
            "start_height": self.blockchain_height + 1,
            "end_height": peer.blockchain_height
        }
        
        self.send_message(sock, request)
    
    def send_message(self, sock: socket.socket, message: Dict):
        """Envia mensagem criptografada"""
        try:
            data = json.dumps(message).encode()
            encrypted_data = self.cipher.encrypt(data)
            sock.send(encrypted_data)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    def decrypt_message(self, encrypted_data: bytes) -> Dict:
        """Descriptografa mensagem"""
        try:
            data = self.cipher.decrypt(encrypted_data)
            return json.loads(data.decode())
        except Exception as e:
            logger.error(f"Erro ao descriptografar mensagem: {e}")
            return {}
    
    def broadcast_transaction(self, transaction: TransactionData):
        """Transmite transação para todos os peers"""
        message = {
            "type": "transaction",
            "transaction": asdict(transaction)
        }
        
        for sock in self.connections.values():
            try:
                self.send_message(sock, message)
            except Exception as e:
                logger.error(f"Erro ao transmitir transação: {e}")
    
    def get_network_status(self) -> Dict:
        """Obtém status da rede P2P"""
        return {
            "node_id": self.node_id,
            "ip_address": self.ip_address,
            "port": self.port,
            "node_type": self.node_type.value,
            "peers_count": len(self.peers),
            "blockchain_height": self.blockchain_height,
            "connections_count": len(self.connections),
            "transaction_pool_size": len(self.transaction_pool),
            "is_running": self.is_running
        }
    
    def add_block(self, block: BlockData):
        """Adiciona bloco ao blockchain local"""
        self.blockchain_data[block.block_number] = block
        self.blockchain_height = max(self.blockchain_height, block.block_number)
        
        # Transmite bloco para peers
        message = {
            "type": "block_data",
            "block": asdict(block)
        }
        
        for sock in self.connections.values():
            try:
                self.send_message(sock, message)
            except Exception as e:
                logger.error(f"Erro ao transmitir bloco: {e}")
    
    def add_transaction(self, transaction: TransactionData):
        """Adiciona transação ao pool local"""
        if transaction not in self.transaction_pool:
            self.transaction_pool.append(transaction)
            self.broadcast_transaction(transaction)

def main():
    """Exemplo de uso do sistema P2P Offline"""
    
    # Cria nós P2P
    node1 = P2POffline("node_001", 8080, NodeType.FULL_NODE)
    node2 = P2POffline("node_002", 8081, NodeType.LIGHT_NODE)
    
    # Inicia redes
    node1.start_network()
    node2.start_network()
    
    try:
        print("=== SISTEMA P2P OFFLINE ===")
        print("Nós iniciados e operando em modo offline")
        print()
        
        # Simula adição de blocos
        block1 = BlockData(
            block_hash="block_001_hash",
            block_number=1,
            timestamp=time.time(),
            transactions=[],
            previous_hash="genesis"
        )
        
        node1.add_block(block1)
        print("Bloco adicionado ao nó 1 e transmitido para rede")
        
        # Simula transações
        tx1 = TransactionData(
            tx_hash="tx_001",
            from_address="address_1",
            to_address="address_2",
            amount=100.0,
            timestamp=time.time(),
            signature="signature_123"
        )
        
        node1.add_transaction(tx1)
        print("Transação adicionada ao nó 1 e transmitida para rede")
        
        # Mostra status
        time.sleep(2)
        
        print("\n=== STATUS DA REDE ===")
        status1 = node1.get_network_status()
        status2 = node2.get_network_status()
        
        print(f"Nó 1: {status1['node_id']} - Altura: {status1['blockchain_height']} - Peers: {status1['peers_count']}")
        print(f"Nó 2: {status2['node_id']} - Altura: {status2['blockchain_height']} - Peers: {status2['peers_count']}")
        
        print("\nSistema P2P offline operacional!")
        print("Pronto para operação em ambientes sem internet")
        
        # Mantém os nós rodando
        while True:
            time.sleep(10)
            print(f"Batimento cardíaco da rede - Nó 1: {len(node1.peers)} peers, Nó 2: {len(node2.peers)} peers")
            
    except KeyboardInterrupt:
        print("\nEncerrando nós P2P...")
        node1.stop_network()
        node2.stop_network()

if __name__ == "__main__":
    main()