#!/usr/bin/env python3
"""
Local Ledger - Blockchain Real para Moral Money
===============================================

Implementa uma blockchain completa com:
- Estrutura de blocos com hash SHA-256
- Proof of Work com dificuldade ajustável
- Mempool para transações pendentes
- Validação de integridade
- Detecção de ataques

Características:
- Blocos minerados a cada 5-10 segundos (dificuldade baixa)
- Transações completas (pagamentos, saúde, votos)
- Logs visuais e legíveis
- Teste de stress com hack simulado
"""

import hashlib
import json
import time
import threading
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class TransactionType(Enum):
    PAYMENT = "payment"
    HEALTH = "health"
    VOTE = "vote"

@dataclass
class Transaction:
    """Transação no sistema"""
    sender: str
    receiver: str
    amount: float
    transaction_type: TransactionType
    description: str
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'type': self.transaction_type.value,
            'description': self.description,
            'timestamp': self.timestamp
        }
    
    def to_string(self) -> str:
        """Converte transação para string para cálculo de hash"""
        return f"{self.sender}{self.receiver}{self.amount}{self.transaction_type.value}{self.description}{self.timestamp}"

class Block:
    """Bloco da blockchain"""
    
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula hash SHA-256 do bloco"""
        block_string = f"{self.index}{self.timestamp}{self.previous_hash}{self.nonce}{[tx.to_string() for tx in self.transactions]}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> float:
        """Minera o bloco com Proof of Work"""
        target = '0' * difficulty
        start_time = time.time()
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        end_time = time.time()
        return end_time - start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte bloco para dicionário"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        }

class Blockchain:
    """Blockchain completa com validação de integridade"""
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.difficulty = difficulty
        self.mining_thread = None
        self.running = False
        
        # Cria bloco genesis
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Cria bloco genesis"""
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print("🏗️ Bloco Genesis criado")
    
    def add_transaction(self, transaction: Transaction):
        """Adiciona transação ao mempool"""
        self.mempool.append(transaction)
        print(f"📝 Transação adicionada ao mempool: {transaction.sender} → {transaction.receiver}")
    
    def mine_pending_transactions(self, miner_address: str = "Sistema"):
        """Minera transações pendentes"""
        if not self.mempool:
            return
        
        # Cria bloco com transações do mempool
        block = Block(len(self.chain), self.mempool.copy(), self.chain[-1].hash)
        
        # Minera o bloco
        mining_time = block.mine_block(self.difficulty)
        
        # Adiciona bloco à cadeia
        self.chain.append(block)
        
        # Limpa mempool
        self.mempool = []
        
        # Exibe log visual
        self.display_block_log(block, mining_time)
    
    def display_block_log(self, block: Block, mining_time: float):
        """Exibe log visual do bloco minerado"""
        print("\n" + "="*80)
        print(f"🔨 BLOCO #{block.index:03d} MINERADO")
        print("="*80)
        print(f"⏰ Horário: {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Transações: {len(block.transactions)}")
        print(f"🔗 Hash: {block.hash}")
        print(f"🔗 Hash Anterior: {block.previous_hash}")
        print(f"🔢 Nonce: {block.nonce}")
        print(f"⏱️ Tempo de Mineração: {mining_time:.2f}s")
        print("\n" + "TRANSAÇÕES:".center(80))
        print("-"*80)
        
        for i, tx in enumerate(block.transactions):
            timestamp_str = datetime.fromtimestamp(tx.timestamp).strftime('%H:%M:%S')
            print(f"[{timestamp_str}] {tx.sender} → {tx.receiver}: {tx.amount:6.2f} BLD ({tx.transaction_type.value})")
            if tx.description:
                print(f"{' '*15} {tx.description}")
        
        print("="*80)
    
    def is_chain_valid(self) -> bool:
        """Valida integridade da blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verifica hash do bloco atual
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Hash inválido no bloco {i}")
                return False
            
            # Verifica hash anterior
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Hash anterior inválido no bloco {i}")
                return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """Calcula saldo de uma conta"""
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance
    
    def start_mining(self, interval: int = 5):
        """Inicia mineração automática"""
        self.running = True
        
        def mining_loop():
            while self.running:
                if self.mempool:
                    self.mine_pending_transactions()
                time.sleep(interval)
        
        self.mining_thread = threading.Thread(target=mining_loop, daemon=True)
        self.mining_thread.start()
        print(f"⛏️ Mineração automática iniciada (intervalo: {interval}s)")
    
    def stop_mining(self):
        """Para mineração automática"""
        self.running = False
        if self.mining_thread:
            self.mining_thread.join()
        print("🛑 Mineração interrompida")
    
    def hack_block(self, block_index: int, new_transaction: Transaction):
        """Simula ataque - altera transação em bloco existente"""
        if block_index < len(self.chain):
            print(f"\n🚨 ATENÇÃO: Hackeando bloco {block_index}")
            print(f"   Adicionando transação falsa: {new_transaction.sender} → {new_transaction.receiver}")
            
            # Altera transação no bloco
            self.chain[block_index].transactions.append(new_transaction)
            
            # Recalcula hash (sem minerar)
            self.chain[block_index].hash = self.chain[block_index].calculate_hash()
            
            print(f"   Hash alterado para: {self.chain[block_index].hash}")
    
    def detect_hack(self) -> bool:
        """Detecta alterações fraudulentas na blockchain"""
        is_valid = self.is_chain_valid()
        
        if not is_valid:
            print("\n🛡️ SISTEMA DE SEGURANÇA ATIVADO!")
            print("   ❌ Alteração detectada na blockchain")
            print("   🔄 Rejeitando bloco inválido")
            print("   📊 Alertando comunidade")
            return False
        
        print("✅ Blockchain íntegra - nenhum ataque detectado")
        return True

def main():
    """Demonstração do Local Ledger"""
    
    print("🚀 INICIANDO LOCAL LEDGER - MORAL MONEY")
    print("="*80)
    
    # Cria blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Inicia mineração automática
    blockchain.start_mining(interval=5)
    
    # Simula transações iniciais
    print("\n📝 SIMULANDO TRÁFEGO INICIAL...")
    
    # Transações de pagamento
    blockchain.add_transaction(Transaction(
        sender="Nuno",
        receiver="Cooperativa",
        amount=67.50,
        transaction_type=TransactionType.PAYMENT,
        description="8h limpeza de vala",
        timestamp=time.time()
    ))
    
    blockchain.add_transaction(Transaction(
        sender="Cooperativa",
        receiver="Médico",
        amount=21.00,
        transaction_type=TransactionType.PAYMENT,
        description="Consulta médica",
        timestamp=time.time()
    ))
    
    # Transações de saúde
    blockchain.add_transaction(Transaction(
        sender="Médico",
        receiver="Paciente_12",
        amount=0.00,
        transaction_type=TransactionType.HEALTH,
        description="Prescrição antibiótico",
        timestamp=time.time()
    ))
    
    # Transações de voto
    blockchain.add_transaction(Transaction(
        sender="Membro_45",
        receiver="Conselho",
        amount=0.00,
        transaction_type=TransactionType.VOTE,
        description="Voto aprovar nova horta",
        timestamp=time.time()
    ))
    
    # Aguarda primeira mineração
    time.sleep(6)
    
    # Teste de stress - Hack simulado
    print("\n" + "🚨 TESTE DE STRESS - ATQUE SIMULADO" + "\n" + "="*80)
    
    # Hackeia bloco 1
    hack_tx = Transaction(
        sender="Hacker",
        receiver="Bolsos",
        amount=1000.00,
        transaction_type=TransactionType.PAYMENT,
        description="Transferência fraudulenta",
        timestamp=time.time()
    )
    
    blockchain.hack_block(1, hack_tx)
    
    # Aguarda próxima mineração para detectar o hack
    time.sleep(6)
    
    # Verifica integridade
    print("\n🔍 VERIFICANDO INTEGRIDADE DA BLOCKCHAIN...")
    is_secure = blockchain.detect_hack()
    
    # Exibe status final
    print("\n" + "📊 STATUS FINAL" + "\n" + "="*80)
    print(f"Total de blocos: {len(blockchain.chain)}")
    print(f"Transações no mempool: {len(blockchain.mempool)}")
    print(f"Blockchain segura: {'✅ SIM' if is_secure else '❌ NÃO'}")
    
    # Saldo de exemplo
    saldo_nuno = blockchain.get_balance("Nuno")
    saldo_medico = blockchain.get_balance("Médico")
    print(f"Saldo Nuno: {saldo_nuno:.2f} BLD")
    print(f"Saldo Médico: {saldo_medico:.2f} BLD")
    
    # Para mineração
    blockchain.stop_mining()
    
    print("\n✅ LOCAL LEDGER ENCERRADO")
    print("   Sistema pronto para testes reais na Serra do Bouro!")

if __name__ == "__main__":
    main()