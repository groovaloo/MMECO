import time
import random
import threading
from substrateinterface import SubstrateInterface, Keypair
from dataclasses import dataclass
from enum import Enum

# --- CONFIGURAÇÃO DE LIGAÇÃO ---
try:
    substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
    print("✅ Conectado ao Nó Polkadot MMECO")
except Exception as e:
    print(f"❌ Erro de ligação: {e}. A simulação correrá em modo offline.")
    substrate = None

class PersonType(Enum):
    WORKER = "worker"
    MEDICAL = "medical"
    FARMER = "farmer"
    TRADER = "trader"
    ADMIN = "admin"

@dataclass
class Person:
    id: str
    name: str
    person_type: PersonType
    keypair: Keypair # Cada pessoa agora tem uma chave criptográfica real

class SimulationAgents:
    def __init__(self):
        self.people = []
        self.running = False
        self.initialize_people()

    def initialize_people(self):
        """Cria 100 pessoas com chaves reais da blockchain."""
        for i in range(100):
            # Gera uma conta real para cada simulação (ex: Alice, Bob, etc.)
            # Para testes, usamos sementes determinísticas
            mnemonic = f"person number {i} secret seed for mmeco community"
            kp = Keypair.create_from_uri(f"//{i}") 
            
            p_type = random.choice(list(PersonType))
            self.people.append(Person(
                id=kp.ss58_address,
                name=f"Membro_{i+1}",
                person_type=p_type,
                keypair=kp
            ))
        print(f"👥 100 Agentes Criptográficos criados.")

    def enviar_para_blockchain(self, person, call_module, call_function, params):
        """Envia a ação do agente para o nó Rust."""
        if not substrate:
            return
        
        payload = substrate.compose_call(
            call_module=call_module,
            call_function=call_function,
            call_params=params
        )
        
        # Assina com a chave privada do agente
        extrinsic = substrate.create_signed_extrinsic(call=payload, keypair=person.keypair)
        
        try:
            receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
            print(f"⛓️  {person.name} -> {call_function} (Hash: {receipt.extrinsic_hash})")
        except Exception as e:
            print(f"⚠️ Erro no envio de {person.name}: {e}")

    def simulate_step(self):
        """Um passo de tempo na vida da comunidade."""
        p1 = random.choice(self.people)
        p2 = random.choice(self.people)
        
        # Exemplo: Transferência de Balanço (Pallet Balances)
        if random.random() > 0.5:
            self.enviar_para_blockchain(
                p1, "Balances", "transfer_allow_death", 
                {"dest": p2.id, "value": 10**10} # 10^10 "plancks"
            )
        
        # Exemplo: Registro de Reputação (Tua Palete)
        else:
            self.enviar_para_blockchain(
                p1, "Reputation", "add_reputation", 
                {"target": p2.id, "amount": random.randint(1, 10)}
            )

    def run(self):
        self.running = True
        while self.running:
            self.simulate_step()
            time.sleep(random.uniform(0.5, 2.0)) # Simula tráfego humano

# --- EXECUÇÃO ---
sim = SimulationAgents()
# sim.run() # Só descomentar quando o nó estiver a correr!
