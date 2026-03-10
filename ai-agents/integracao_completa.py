#!/usr/bin/env python3
"""
Sistema de Integração Completa para Moral Money

Integra todos os componentes do sistema:
- IA de Auditoria
- Conselho dos 5
- Equivalência Ética
- Governança Horizontal
- P2P Offline

Cria um fluxo completo de operação do sistema Moral Money.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time

# Importa os módulos implementados
from ia_auditoria import MoralMoneyIA
from conselho_5 import ConselhoDos5
from equivalencia_etica import EquivalenciaEtica, EthicalContribution, ContributionType
from governanca_horizontal import GovernancaHorizontal, GovernanceLevel, DecisionType
from p2p_offline import P2POffline, NodeType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemState(Enum):
    INITIALIZING = "Initializing"
    OPERATIONAL = "Operational"
    SYNCING = "Syncing"
    ERROR = "Error"
    OFFLINE = "Offline"

@dataclass
class SystemStatus:
    state: SystemState
    blockchain_height: int
    active_peers: int
    pending_processes: int
    total_buildcoins: float
    last_sync: float

class SistemaIntegrado:
    """
    Sistema Integrado de Moral Money
    
    Coordenador de todos os componentes do sistema:
    1. IA de Auditoria - Validação automática de contribuições
    2. Conselho dos 5 - Governança soberana
    3. Equivalência Ética - Distribuição justa de Buildcoins
    4. Governança Horizontal - Decisões baseadas em expertise
    5. P2P Offline - Comunicação descentralizada
    """
    
    def __init__(self, node_id: str = "moral_money_node_001"):
        self.node_id = node_id
        self.state = SystemState.INITIALIZING
        
        # Componentes do sistema
        self.ia_auditoria = None
        self.conselho_5 = None
        self.equivalencia_etica = None
        self.governanca = None
        self.p2p_network = None
        
        # Estado do sistema
        self.status = SystemStatus(
            state=SystemState.INITIALIZING,
            blockchain_height=0,
            active_peers=0,
            pending_processes=0,
            total_buildcoins=0.0,
            last_sync=0.0
        )
        
        # Threads de operação
        self.main_loop_task = None
        self.sync_task = None
        
        logger.info(f"Sistema Integrado iniciado: {self.node_id}")
    
    async def initialize_system(self):
        """Inicializa todos os componentes do sistema"""
        logger.info("=== INICIALIZANDO SISTEMA INTEGRADO ===")
        
        try:
            # 1. Inicializa P2P Offline
            logger.info("1. Inicializando rede P2P Offline...")
            self.p2p_network = P2POffline(self.node_id, 8080, NodeType.FULL_NODE)
            self.p2p_network.start_network()
            await asyncio.sleep(2)
            
            # 2. Inicializa IA de Auditoria
            logger.info("2. Inicializando IA de Auditoria...")
            self.ia_auditoria = MoralMoneyIA("http://localhost:9933")
            
            # 3. Inicializa Conselho dos 5
            logger.info("3. Inicializando Conselho dos 5...")
            self.conselho_5 = ConselhoDos5("http://localhost:9933")
            
            # 4. Inicializa Equivalência Ética
            logger.info("4. Inicializando Equivalência Ética...")
            self.equivalencia_etica = EquivalenciaEtica("http://localhost:9933")
            
            # 5. Inicializa Governança Horizontal
            logger.info("5. Inicializando Governança Horizontal...")
            self.governanca = GovernancaHorizontal("http://localhost:9933")
            
            # Atualiza estado
            self.state = SystemState.OPERATIONAL
            self.status.state = SystemState.OPERATIONAL
            self.status.last_sync = time.time()
            
            logger.info("=== SISTEMA INTEGRADO INICIALIZADO COM SUCESSO ===")
            logger.info("Todos os componentes estão operacionais!")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do sistema: {e}")
            self.state = SystemState.ERROR
            return False
    
    async def start_main_loop(self):
        """Inicia o loop principal do sistema"""
        if self.main_loop_task is None:
            self.main_loop_task = asyncio.create_task(self.main_loop())
            logger.info("Loop principal do sistema iniciado")
    
    async def main_loop(self):
        """Loop principal de operação do sistema"""
        while self.state == SystemState.OPERATIONAL:
            try:
                # Atualiza status do sistema
                await self.update_system_status()
                
                # Verifica sincronização P2P
                await self.check_p2p_sync()
                
                # Processa auditorias pendentes
                await self.process_pending_audits()
                
                # Verifica governança
                await self.check_governance_proposals()
                
                # Atualiza estatísticas
                await self.update_statistics()
                
                # Dorme por um intervalo
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(5)
    
    async def update_system_status(self):
        """Atualiza status do sistema"""
        try:
            if self.p2p_network:
                p2p_status = self.p2p_network.get_network_status()
                self.status.blockchain_height = p2p_status["blockchain_height"]
                self.status.active_peers = p2p_status["peers_count"]
                self.status.last_sync = time.time()
            
            # Atualiza total de Buildcoins (simulação)
            self.status.total_buildcoins += 0.1  # Simulação de emissão
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
    
    async def check_p2p_sync(self):
        """Verifica sincronização da rede P2P"""
        if self.p2p_network and self.status.active_peers > 0:
            # Verifica se há peers para sincronizar
            peers = self.p2p_network.peers
            for peer_id, peer in peers.items():
                if peer.blockchain_height > self.status.blockchain_height:
                    logger.info(f"Sincronizando com peer {peer_id}")
                    # A sincronização é automática no P2P
    
    async def process_pending_audits(self):
        """Processa auditorias pendentes"""
        try:
            # Simula processos pendentes
            pending_processes = [
                {
                    "id": 1001,
                    "domain": ContributionType.CONSTRUCTION,
                    "description": "Construção de habitação comunitária",
                    "buildcoin_value": 50000,
                    "participants": ["worker_001", "worker_002", "investor_001"]
                }
            ]
            
            for process_data in pending_processes:
                logger.info(f"Processando auditoria para processo {process_data['id']}")
                
                # Executa auditoria completa
                if self.ia_auditoria:
                    try:
                        # Simula auditoria
                        audit_result = "Approved"
                        confidence = 0.85
                        
                        logger.info(f"Auditoria concluída: {audit_result} (confiança: {confidence:.2f})")
                        
                    except Exception as e:
                        logger.error(f"Erro na auditoria: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao processar auditorias: {e}")
    
    async def check_governance_proposals(self):
        """Verifica propostas de governança"""
        try:
            if self.governanca:
                active_proposals = self.governanca.get_active_proposals()
                
                for proposal in active_proposals:
                    logger.info(f"Proposta ativa: {proposal['title']}")
                    
                    # Simula votação
                    if len(proposal['votes_count']) < 3:
                        # Simula votos do conselho
                        council = self.conselho_5.select_council(proposal['level'], proposal['id'])
                        
                        for member in council[:3]:  # Primeiros 3 votam
                            self.governanca.cast_governance_vote(
                                proposal['id'], 
                                member.account_id, 
                                "approve"
                            )
                        
                        logger.info(f"Votos registrados para proposta {proposal['id']}")
                        
        except Exception as e:
            logger.error(f"Erro ao verificar governança: {e}")
    
    async def update_statistics(self):
        """Atualiza estatísticas do sistema"""
        try:
            # Estatísticas de equivalência ética
            if self.equivalencia_etica:
                # Simula contribuições
                contributions = [
                    EthicalContribution(
                        contributor_id="worker_001",
                        contribution_type=ContributionType.CONSTRUCTION,
                        work_hours=1000,
                        skill_level=0.8,
                        impact_factor=1.5,
                        age=35,
                        capital_invested=0.0,
                        ethical_score=0.0
                    ),
                    EthicalContribution(
                        contributor_id="investor_001",
                        contribution_type=ContributionType.CONSTRUCTION,
                        work_hours=50,
                        skill_level=0.9,
                        impact_factor=1.2,
                        age=55,
                        capital_invested=2000000.0,
                        ethical_score=0.0
                    )
                ]
                
                distribution = self.equivalencia_etica.analyze_contribution_distribution(contributions)
                
                logger.info(f"Distribuição ética: {distribution['ethical_ratio']:.2%} válida")
                logger.info(f"Buildcoins alocados: {distribution['total_buildcoins_allocated']:.2f}")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    async def submit_ethical_contribution(self, contribution: EthicalContribution):
        """Submete contribuição para validação ética"""
        try:
            if self.equivalencia_etica:
                calculation = self.equivalencia_etica.calculate_ethical_equivalence(contribution)
                
                if calculation.ethical_validation:
                    logger.info(f"Contribuição ética aprovada: {contribution.contributor_id}")
                    logger.info(f"Buildcoins alocados: {calculation.buildcoin_allocation:.2f}")
                    
                    # Integra com blockchain (simulação)
                    if self.p2p_network:
                        # Simula transação de Buildcoin
                        from p2p_offline import TransactionData
                        tx = TransactionData(
                            tx_hash=f"tx_{int(time.time())}",
                            from_address="system",
                            to_address=contribution.contributor_id,
                            amount=calculation.buildcoin_allocation,
                            timestamp=time.time(),
                            signature="signature_123"
                        )
                        self.p2p_network.add_transaction(tx)
                        logger.info(f"Transação de Buildcoin registrada")
                
                else:
                    logger.warning(f"Contribuição não ética: {contribution.contributor_id}")
                
                return calculation
                
        except Exception as e:
            logger.error(f"Erro ao submeter contribuição: {e}")
            return None
    
    async def create_governance_proposal(self, title: str, description: str, 
                                       governance_level: GovernanceLevel,
                                       decision_type: DecisionType):
        """Cria proposta de governança"""
        try:
            if self.governanca:
                proposal_id = self.governanca.submit_proposal(
                    proposer=self.node_id,
                    title=title,
                    description=description,
                    governance_level=governance_level,
                    decision_type=decision_type
                )
                
                logger.info(f"Proposta de governança criada: {proposal_id}")
                return proposal_id
                
        except Exception as e:
            logger.error(f"Erro ao criar proposta: {e}")
            return None
    
    def get_system_health(self) -> Dict:
        """Obtém saúde do sistema"""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "blockchain_height": self.status.blockchain_height,
            "active_peers": self.status.active_peers,
            "pending_processes": self.status.pending_processes,
            "total_buildcoins": self.status.total_buildcoins,
            "last_sync": self.status.last_sync,
            "components": {
                "ia_auditoria": self.ia_auditoria is not None,
                "conselho_5": self.conselho_5 is not None,
                "equivalencia_etica": self.equivalencia_etica is not None,
                "governanca": self.governanca is not None,
                "p2p_network": self.p2p_network is not None
            }
        }
    
    async def shutdown(self):
        """Encerra o sistema integrado"""
        logger.info("=== ENCERRANDO SISTEMA INTEGRADO ===")
        
        self.state = SystemState.OFFLINE
        
        # Para tarefas
        if self.main_loop_task:
            self.main_loop_task.cancel()
        
        # Encerra P2P
        if self.p2p_network:
            self.p2p_network.stop_network()
        
        logger.info("Sistema integrado encerrado")

async def main():
    """Exemplo de uso do Sistema Integrado"""
    
    # Cria sistema integrado
    sistema = SistemaIntegrado("moral_money_central")
    
    # Inicializa
    success = await sistema.initialize_system()
    if not success:
        logger.error("Falha na inicialização do sistema")
        return
    
    # Inicia loop principal
    await sistema.start_main_loop()
    
    try:
        print("=== SISTEMA INTEGRADO MORAL MONEY ===")
        print("Todos os componentes estão operacionais!")
        print()
        
        # Mostra status inicial
        health = sistema.get_system_health()
        print("=== SAÚDE DO SISTEMA ===")
        print(f"Estado: {health['state']}")
        print(f"Nó: {health['node_id']}")
        print(f"Altura Blockchain: {health['blockchain_height']}")
        print(f"Peers Ativos: {health['active_peers']}")
        print(f"Buildcoins Totais: {health['total_buildcoins']:.2f}")
        print()
        
        # Simula contribuições éticas
        print("=== SIMULANDO CONTRIBUIÇÕES ÉTICAS ===")
        
        worker_contribution = EthicalContribution(
            contributor_id="trabalhador_001",
            contribution_type=ContributionType.CONSTRUCTION,
            work_hours=2000,
            skill_level=0.8,
            impact_factor=1.5,
            age=30,
            capital_invested=0.0,
            ethical_score=0.0
        )
        
        investor_contribution = EthicalContribution(
            contributor_id="investidor_001",
            contribution_type=ContributionType.CONSTRUCTION,
            work_hours=100,
            skill_level=0.9,
            impact_factor=1.2,
            age=60,
            capital_invested=4000000.0,
            ethical_score=0.0
        )
        
        # Processa contribuições
        worker_result = await sistema.submit_ethical_contribution(worker_contribution)
        investor_result = await sistema.submit_ethical_contribution(investor_contribution)
        
        if worker_result and investor_result:
            print(f"Trabalhador: {worker_result.buildcoin_allocation:.2f} Buildcoins")
            print(f"Investidor: {investor_result.buildcoin_allocation:.2f} Buildcoins")
            print("Equivalência Ética implementada com sucesso!")
        
        print()
        
        # Cria proposta de governança
        print("=== CRIANDO PROPOSTA DE GOVERNANÇA ===")
        
        proposal_id = await sistema.create_governance_proposal(
            title="Implementação de Equivalência Ética",
            description="Implementar o princípio de Equivalência Ética em todos os domínios",
            governance_level=GovernanceLevel.CONSTITUTIONAL,
            decision_type=DecisionType.AMENDMENT
        )
        
        if proposal_id:
            print(f"Proposta criada: {proposal_id}")
        
        print()
        print("=== SISTEMA OPERACIONAL ===")
        print("Pronto para operação completa do Moral Money!")
        
        # Mantém o sistema rodando
        while True:
            await asyncio.sleep(30)
            health = sistema.get_system_health()
            print(f"Batimento cardíaco - Peers: {health['active_peers']}, Altura: {health['blockchain_height']}")
            
    except KeyboardInterrupt:
        print("\nEncerrando sistema...")
        await sistema.shutdown()

if __name__ == "__main__":
    asyncio.run(main())