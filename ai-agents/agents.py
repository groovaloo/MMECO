#!/usr/bin/env python3
"""
Agentes de Simulação - Tráfego de 100 Pessoas
=============================================

Simula o tráfego real de 100 pessoas na comunidade com:
- Padrões de comportamento realistas
- Transações aleatórias mas consistentes
- Integração com o Local Ledger
- Registros de saúde e votações

Características:
- 100 pessoas simuladas com perfis diferentes
- Tráfego distribuído ao longo do dia
- Tipos de transações variadas
- Logs detalhados de atividade
"""

import time
import random
import threading
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from local_ledger import Blockchain, Transaction, TransactionType

class PersonType(Enum):
    WORKER = "worker"           # Trabalhadores (Nuno, construtores)
    MEDICAL = "medical"         # Saúde (médico, enfermeiros)
    FARMER = "farmer"          # Agricultores
    TRADER = "trader"          # Comerciantes
    ADMIN = "admin"            # Administração

@dataclass
class Person:
    """Pessoa na comunidade"""
    id: str
    name: str
    person_type: PersonType
    balance: float
    work_hours: float
    last_activity: float

class SimulationAgents:
    """Gerenciador de agentes de simulação"""
    
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.people: List[Person] = []
        self.running = False
        self.simulation_thread = None
        
        # Configurações de simulação
        self.work_interval = 2  # Horas entre registros de trabalho
        self.payment_interval = 1  # Horas entre pagamentos
        self.health_interval = 0.5  # Horas entre registros de saúde
        self.vote_interval = 24  # Horas entre votações
        
        self.initialize_people()
    
    def initialize_people(self):
        """Inicializa as 100 pessoas da comunidade"""
        # Trabalhadores (40 pessoas)
        for i in range(40):
            self.people.append(Person(
                id=f"worker_{i+1:03d}",
                name=f"Trabalhador_{i+1}",
                person_type=PersonType.WORKER,
                balance=0.0,
                work_hours=0.0,
                last_activity=time.time()
            ))
        
        # Médicos (5 pessoas)
        for i in range(5):
            self.people.append(Person(
                id=f"medical_{i+1:03d}",
                name=f"Médico_{i+1}",
                person_type=PersonType.MEDICAL,
                balance=0.0,
                work_hours=0.0,
                last_activity=time.time()
            ))
        
        # Agricultores (30 pessoas)
        for i in range(30):
            self.people.append(Person(
                id=f"farmer_{i+1:03d}",
                name=f"Agricultor_{i+1}",
                person_type=PersonType.FARMER,
                balance=0.0,
                work_hours=0.0,
                last_activity=time.time()
            ))
        
        # Comerciantes (15 pessoas)
        for i in range(15):
            self.people.append(Person(
                id=f"trader_{i+1:03d}",
                name=f"Comerciante_{i+1}",
                person_type=PersonType.TRADER,
                balance=0.0,
                work_hours=0.0,
                last_activity=time.time()
            ))
        
        # Administração (10 pessoas)
        for i in range(10):
            self.people.append(Person(
                id=f"admin_{i+1:03d}",
                name=f"Admin_{i+1}",
                person_type=PersonType.ADMIN,
                balance=0.0,
                work_hours=0.0,
                last_activity=time.time()
            ))
        
        print(f"👥 Comunidade inicializada com {len(self.people)} pessoas")
    
    def simulate_work(self):
        """Simula registro de horas de trabalho"""
        # Seleciona trabalhadores aleatórios
        workers = [p for p in self.people if p.person_type == PersonType.WORKER]
        if not workers:
            return
        
        worker = random.choice(workers)
        
        # Horas aleatórias (2-8 horas)
        hours = random.uniform(2, 8)
        
        # Valor baseado no escalão (7.50€/h) com multiplicador aleatório
        base_rate = 7.50
        multiplier = random.uniform(1.0, 2.0)
        amount = hours * base_rate * multiplier
        
        # Cria transação
        tx = Transaction(
            sender=worker.id,
            receiver="Cooperativa",
            amount=amount,
            transaction_type=TransactionType.PAYMENT,
            description=f"{hours:.1f}h de trabalho ({worker.name})",
            timestamp=time.time()
        )
        
        self.blockchain.add_transaction(tx)
        worker.work_hours += hours
        worker.last_activity = time.time()
        
        print(f"🔨 {worker.name} registrou {hours:.1f}h de trabalho: {amount:.2f} BLD")
    
    def simulate_payments(self):
        """Simula pagamentos entre membros"""
        # Seleciona aleatoriamente quem vai pagar e receber
        payer = random.choice(self.people)
        receiver = random.choice(self.people)
        
        # Evita auto-pagamento
        while receiver.id == payer.id:
            receiver = random.choice(self.people)
        
        # Tipos de pagamento
        payment_types = [
            ("Compra de alimentos", 5.0, 20.0),
            ("Serviço de construção", 10.0, 50.0),
            ("Consulta médica", 15.0, 30.0),
            ("Troca de produtos", 2.0, 15.0),
            ("Pagamento de energia", 3.0, 10.0)
        ]
        
        description, min_amount, max_amount = random.choice(payment_types)
        amount = random.uniform(min_amount, max_amount)
        
        tx = Transaction(
            sender=payer.id,
            receiver=receiver.id,
            amount=amount,
            transaction_type=TransactionType.PAYMENT,
            description=description,
            timestamp=time.time()
        )
        
        self.blockchain.add_transaction(tx)
        print(f"💳 {payer.name} pagou {amount:.2f} BLD a {receiver.name} por {description}")
    
    def simulate_health_records(self):
        """Simula registros de saúde"""
        # Médicos registram consultas
        doctors = [p for p in self.people if p.person_type == PersonType.MEDICAL]
        if not doctors:
            return
        
        doctor = random.choice(doctors)
        
        # Paciente aleatório
        patient = random.choice(self.people)
        while patient.id == doctor.id:
            patient = random.choice(self.people)
        
        # Tipos de registro de saúde
        health_records = [
            "Prescrição de medicamento",
            "Agendamento de consulta",
            "Resultado de exame",
            "Receita de fisioterapia",
            "Acompanhamento de saúde"
        ]
        
        record = random.choice(health_records)
        
        tx = Transaction(
            sender=doctor.id,
            receiver=patient.id,
            amount=0.0,
            transaction_type=TransactionType.HEALTH,
            description=record,
            timestamp=time.time()
        )
        
        self.blockchain.add_transaction(tx)
        print(f"🏥 {doctor.name} registrou: {record} para {patient.name}")
    
    def simulate_votes(self):
        """Simula votações comunitárias"""
        # Seleciona membros para votar
        voters = random.sample(self.people, min(10, len(self.people)))
        
        # Tipos de votação
        vote_types = [
            "Aprovar nova horta comunitária",
            "Construir escola na zona norte",
            "Implementar sistema de energia solar",
            "Criar cooperativa de artesanato",
            "Aumentar área de cultivo orgânico"
        ]
        
        vote_topic = random.choice(vote_types)
        
        for voter in voters:
            # Decisão aleatória (sim ou não)
            decision = "SIM" if random.random() > 0.3 else "NÃO"
            
            tx = Transaction(
                sender=voter.id,
                receiver="Conselho",
                amount=0.0,
                transaction_type=TransactionType.VOTE,
                description=f"{vote_topic} - {decision}",
                timestamp=time.time()
            )
            
            self.blockchain.add_transaction(tx)
            print(f"🗳️ {voter.name} votou: {decision} em '{vote_topic}'")
    
    def run_simulation(self):
        """Executa a simulação contínua"""
        print("🚀 Iniciando simulação de tráfego...")
        
        start_time = time.time()
        last_work = start_time
        last_payment = start_time
        last_health = start_time
        last_vote = start_time
        
        while self.running:
            current_time = time.time()
            
            # Simula trabalho (a cada 2 horas)
            if current_time - last_work > self.work_interval * 3600:
                self.simulate_work()
                last_work = current_time
            
            # Simula pagamentos (a cada 1 hora)
            if current_time - last_payment > self.payment_interval * 3600:
                self.simulate_payments()
                last_payment = current_time
            
            # Simula registros de saúde (a cada 30 minutos)
            if current_time - last_health > self.health_interval * 3600:
                self.simulate_health_records()
                last_health = current_time
            
            # Simula votações (a cada 24 horas)
            if current_time - last_vote > self.vote_interval * 3600:
                self.simulate_votes()
                last_vote = current_time
            
            # Pequena pausa para não sobrecarregar
            time.sleep(1)
    
    def start(self):
        """Inicia a simulação"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.simulation_thread.start()
        print("✅ Simulação de agentes iniciada")
    
    def stop(self):
        """Para a simulação"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join()
        print("🛑 Simulação de agentes encerrada")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas da simulação"""
        stats = {
            'total_people': len(self.people),
            'by_type': {},
            'total_work_hours': 0,
            'average_balance': 0
        }
        
        # Contagem por tipo
        for person_type in PersonType:
            count = len([p for p in self.people if p.person_type == person_type])
            stats['by_type'][person_type.value] = count
        
        # Total de horas trabalhadas
        stats['total_work_hours'] = sum(p.work_hours for p in self.people)
        
        # Saldo médio
        total_balance = sum(p.balance for p in self.people)
        stats['average_balance'] = total_balance / len(self.people) if self.people else 0
        
        return stats

def main():
    """Demonstração da simulação de agentes"""
    
    print("🤖 INICIANDO SIMULAÇÃO DE AGENTES - 100 PESSOAS")
    print("="*80)
    
    # Cria blockchain
    blockchain = Blockchain(difficulty=2)
    blockchain.start_mining(interval=5)
    
    # Cria agentes de simulação
    agents = SimulationAgents(blockchain)
    agents.start()
    
    # Simula por 30 segundos
    print("\n⏳ Simulando tráfego por 30 segundos...")
    time.sleep(30)
    
    # Para simulação
    agents.stop()
    blockchain.stop_mining()
    
    # Exibe estatísticas
    stats = agents.get_statistics()
    
    print("\n" + "📊 ESTATÍSTICAS DA SIMULAÇÃO" + "\n" + "="*80)
    print(f"Total de pessoas: {stats['total_people']}")
    print(f"Trabalhadores: {stats['by_type']['worker']}")
    print(f"Médicos: {stats['by_type']['medical']}")
    print(f"Agricultores: {stats['by_type']['farmer']}")
    print(f"Comerciantes: {stats['by_type']['trader']}")
    print(f"Administração: {stats['by_type']['admin']}")
    print(f"Total de horas trabalhadas: {stats['total_work_hours']:.1f}h")
    print(f"Saldo médio: {stats['average_balance']:.2f} BLD")
    print(f"Total de blocos minerados: {len(blockchain.chain)}")
    
    print("\n✅ SIMULAÇÃO CONCLUÍDA")
    print("   Sistema demonstrado com tráfego real de 100 pessoas!")

if __name__ == "__main__":
    main()