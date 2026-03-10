#!/usr/bin/env python3
"""
Sistema de Governança Horizontal para Moral Money

Implementa o sistema de governança baseado em reputação por domínio.
Totalmente descentralizado, sem pontos de falha centralizados.

Princípios:
- Decisões baseadas em expertise, não em poder econômico
- Transparência total
- Imparcialidade garantida
- Soberania das decisões do conselho dos 5
"""

import json
import requests
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GovernanceLevel(Enum):
    COMMUNITY = "Community"
    DOMAIN = "Domain"
    SYSTEM = "System"
    CONSTITUTIONAL = "Constitutional"

class DecisionType(Enum):
    PROPOSAL = "Proposal"
    AMENDMENT = "Amendment"
    EMERGENCY = "Emergency"
    ROUTINE = "Routine"

class VoteResult(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    DELEGATED = "Delegated"
    INVALID = "Invalid"

@dataclass
class GovernanceProposal:
    proposal_id: str
    title: str
    description: str
    proposer: str
    governance_level: GovernanceLevel
    decision_type: DecisionType
    created_at: datetime
    expires_at: datetime
    required_quorum: float
    required_majority: float
    votes: Dict[str, str]
    status: str

@dataclass
class DomainExpert:
    account_id: str
    domain: str
    reputation: int
    expertise_score: float
    last_activity: datetime

@dataclass
class GovernanceDecision:
    decision_id: str
    proposal_id: str
    governance_level: GovernanceLevel
    decision_type: DecisionType
    result: VoteResult
    confidence: float
    council_members: List[str]
    justification: str
    created_at: datetime

class GovernancaHorizontal:
    """
    Sistema de Governança Horizontal
    
    Características:
    1. Baseado em reputação por domínio
    2. Decisões soberanas do conselho dos 5
    3. Transparência total
    4. Imparcialidade garantida
    5. Sem pontos de falha centralizados
    """
    
    def __init__(self, rpc_endpoint: str = "http://localhost:9933"):
        self.rpc_endpoint = rpc_endpoint
        self.proposals = {}
        self.experts_cache = {}
        self.decisions = {}
        
    def submit_proposal(self, proposer: str, title: str, description: str, 
                       governance_level: GovernanceLevel, decision_type: DecisionType,
                       required_quorum: float = 0.5, required_majority: float = 0.6) -> str:
        """
        Submete uma proposta de governança
        
        Tipos de propostas:
        - PROPOSAL: Propostas regulares
        - AMENDMENT: Emendas constitucionais (requer nível Constitutional)
        - EMERGENCY: Decisões de emergência (tempo reduzido)
        - ROUTINE: Decisões rotineiras (tempo reduzido)
        """
        proposal_id = self.generate_proposal_id(title, proposer)
        
        # Validar nível de governança
        if not self.validate_governance_level(proposer, governance_level):
            raise ValueError(f"Proposer não tem autoridade para nível {governance_level}")
        
        # Definir tempo de expiração baseado no tipo
        expires_at = self.calculate_expiration_time(decision_type)
        
        proposal = GovernanceProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            governance_level=governance_level,
            decision_type=decision_type,
            created_at=datetime.now(),
            expires_at=expires_at,
            required_quorum=required_quorum,
            required_majority=required_majority,
            votes={},
            status="Pending"
        )
        
        self.proposals[proposal_id] = proposal
        logger.info(f"Proposta submetida: {proposal_id} por {proposer}")
        
        return proposal_id
    
    def validate_governance_level(self, proposer: str, level: GovernanceLevel) -> bool:
        """Valida se o proponente tem autoridade para o nível de governança"""
        try:
            # Consulta reputação do proponente
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_getReputation",
                "params": [proposer],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            reputation = response.json()['result']
            
            # Requisitos de reputação por nível
            requirements = {
                GovernanceLevel.COMMUNITY: 1000,
                GovernanceLevel.DOMAIN: 5000,
                GovernanceLevel.SYSTEM: 25000,
                GovernanceLevel.CONSTITUTIONAL: 100000
            }
            
            return reputation >= requirements.get(level, 0)
            
        except Exception as e:
            logger.error(f"Erro ao validar nível de governança: {e}")
            return False
    
    def calculate_expiration_time(self, decision_type: DecisionType) -> datetime:
        """Calcula tempo de expiração baseado no tipo de decisão"""
        base_duration = timedelta(days=7)  # 7 dias padrão
        
        multipliers = {
            DecisionType.ROUTINE: 0.5,      # 3.5 dias
            DecisionType.PROPOSAL: 1.0,     # 7 dias
            DecisionType.EMERGENCY: 0.25,   # 1.75 dias
            DecisionType.AMENDMENT: 2.0     # 14 dias
        }
        
        duration = base_duration * multipliers.get(decision_type, 1.0)
        return datetime.now() + duration
    
    def get_domain_experts(self, domain: str, min_reputation: int = 1000) -> List[DomainExpert]:
        """Obtém especialistas em um domínio específico"""
        try:
            # Consulta especialistas no blockchain
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_selectTopExperts",
                "params": [domain],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            experts_data = response.json()['result']
            
            experts = []
            for data in experts_data:
                if data['reputation'] >= min_reputation:
                    expert = DomainExpert(
                        account_id=data['account'],
                        domain=domain,
                        reputation=data['reputation'],
                        expertise_score=self.calculate_expertise_score(data['reputation']),
                        last_activity=datetime.now()  # Simplificado
                    )
                    experts.append(expert)
            
            return experts
            
        except Exception as e:
            logger.error(f"Erro ao obter especialistas: {e}")
            return []
    
    def calculate_expertise_score(self, reputation: int) -> float:
        """Calcula score de expertise baseado na reputação"""
        max_rep = 1_000_000
        return min(reputation / max_rep, 1.0)
    
    def form_governance_council(self, proposal_id: str) -> List[str]:
        """
        Forma o conselho de governança para uma proposta
        
        Baseado no domínio da proposta e reputação dos especialistas
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return []
        
        # Para propostas de nível constitucional, usa especialistas de todos os domínios
        if proposal.governance_level == GovernanceLevel.CONSTITUTIONAL:
            return self.form_constitutional_council()
        
        # Para outros níveis, usa especialistas do domínio relevante
        domain_experts = self.get_domain_experts(proposal.governance_level.value.lower())
        return [expert.account_id for expert in domain_experts[:5]]
    
    def form_constitutional_council(self) -> List[str]:
        """
        Forma conselho constitucional com especialistas de todos os domínios
        
        Requer os top especialistas de cada um dos 6 domínios principais
        """
        domains = ["construction", "agriculture", "energy", "governance", "health", "logistics"]
        council_members = []
        
        for domain in domains:
            experts = self.get_domain_experts(domain)
            if experts:
                council_members.append(experts[0].account_id)  # Top expert de cada domínio
        
        return council_members[:6]  # Máximo 6 membros (um por domínio)
    
    def cast_governance_vote(self, proposal_id: str, voter_id: str, vote: str) -> bool:
        """Registra voto em uma proposta de governança"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        # Verifica se o votante é especialista qualificado
        if not self.is_qualified_voter(voter_id, proposal.governance_level):
            return False
        
        # Verifica se já votou
        if voter_id in proposal.votes:
            return False
        
        # Registra voto
        proposal.votes[voter_id] = vote
        logger.info(f"Voto registrado: {voter_id} -> {vote}")
        
        return True
    
    def is_qualified_voter(self, voter_id: str, governance_level: GovernanceLevel) -> bool:
        """Verifica se o votante é qualificado para o nível de governança"""
        try:
            # Consulta reputação do votante
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_getReputation",
                "params": [voter_id],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            reputation = response.json()['result']
            
            # Requisitos de reputação para votação
            requirements = {
                GovernanceLevel.COMMUNITY: 500,
                GovernanceLevel.DOMAIN: 2000,
                GovernanceLevel.SYSTEM: 10000,
                GovernanceLevel.CONSTITUTIONAL: 50000
            }
            
            return reputation >= requirements.get(governance_level, 0)
            
        except Exception as e:
            logger.error(f"Erro ao validar votante: {e}")
            return False
    
    def calculate_governance_result(self, proposal_id: str) -> Tuple[VoteResult, float, str]:
        """Calcula resultado da votação de governança"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return VoteResult.INVALID, 0.0, "Proposta não encontrada"
        
        # Verifica se a votação expirou
        if datetime.now() < proposal.expires_at:
            return VoteResult.INVALID, 0.0, "Votação ainda em andamento"
        
        # Contagem de votos ponderados
        approve_weight = 0.0
        reject_weight = 0.0
        abstain_weight = 0.0
        
        for voter_id, vote in proposal.votes.items():
            voter_weight = self.get_voter_weight(voter_id, proposal.governance_level)
            
            if vote.lower() == "approve":
                approve_weight += voter_weight
            elif vote.lower() == "reject":
                reject_weight += voter_weight
            elif vote.lower() == "abstain":
                abstain_weight += voter_weight
        
        total_weight = approve_weight + reject_weight + abstain_weight
        
        if total_weight == 0:
            return VoteResult.INVALID, 0.0, "Nenhum voto registrado"
        
        # Verifica quórum
        quorum_met = total_weight >= proposal.required_quorum
        
        if not quorum_met:
            return VoteResult.INVALID, 0.0, "Quórum não atingido"
        
        # Cálculo de maioria
        approve_ratio = approve_weight / total_weight
        reject_ratio = reject_weight / total_weight
        
        # Decisão
        if approve_ratio >= proposal.required_majority:
            result = VoteResult.APPROVED
            confidence = approve_ratio
            justification = f"Aprovado com {approve_ratio:.2%} de apoio"
        elif reject_ratio >= (1.0 - proposal.required_majority):
            result = VoteResult.REJECTED
            confidence = reject_ratio
            justification = f"Rejeitado com {reject_ratio:.2%} de rejeição"
        else:
            result = VoteResult.DELEGATED
            confidence = max(approve_ratio, reject_ratio)
            justification = "Decisão delegada ao conselho dos 5"
        
        # Registra decisão
        decision = GovernanceDecision(
            decision_id=self.generate_decision_id(proposal_id),
            proposal_id=proposal_id,
            governance_level=proposal.governance_level,
            decision_type=proposal.decision_type,
            result=result,
            confidence=confidence,
            council_members=self.form_governance_council(proposal_id),
            justification=justification,
            created_at=datetime.now()
        )
        
        self.decisions[decision.decision_id] = decision
        proposal.status = "Decided"
        
        return result, confidence, justification
    
    def get_voter_weight(self, voter_id: str, governance_level: GovernanceLevel) -> float:
        """Calcula peso do voto baseado na reputação e nível de governança"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_getReputation",
                "params": [voter_id],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            reputation = response.json()['result']
            
            # Peso baseado na reputação
            max_rep = 1_000_000
            base_weight = reputation / max_rep
            
            # Ajuste por nível de governança
            level_multipliers = {
                GovernanceLevel.COMMUNITY: 1.0,
                GovernanceLevel.DOMAIN: 1.5,
                GovernanceLevel.SYSTEM: 2.0,
                GovernanceLevel.CONSTITUTIONAL: 3.0
            }
            
            return base_weight * level_multipliers.get(governance_level, 1.0)
            
        except Exception as e:
            logger.error(f"Erro ao calcular peso do voto: {e}")
            return 0.0
    
    def get_governance_statistics(self) -> Dict:
        """Obtém estatísticas do sistema de governança"""
        total_proposals = len(self.proposals)
        active_proposals = sum(1 for p in self.proposals.values() 
                             if p.status == "Pending" and p.expires_at > datetime.now())
        decided_proposals = sum(1 for p in self.proposals.values() if p.status == "Decided")
        
        # Distribuição por nível
        level_distribution = {}
        for level in GovernanceLevel:
            level_distribution[level.value] = sum(1 for p in self.proposals.values() 
                                                if p.governance_level == level)
        
        # Distribuição por tipo
        type_distribution = {}
        for decision_type in DecisionType:
            type_distribution[decision_type.value] = sum(1 for p in self.proposals.values() 
                                                       if p.decision_type == decision_type)
        
        return {
            "total_proposals": total_proposals,
            "active_proposals": active_proposals,
            "decided_proposals": decided_proposals,
            "level_distribution": level_distribution,
            "type_distribution": type_distribution,
            "total_decisions": len(self.decisions)
        }
    
    def validate_constitutional_amendment(self, proposal_id: str) -> bool:
        """
        Valida emenda constitucional
        
        Emendas constitucionais requerem:
        - Nível Constitutional
        - Quórum de 75%
        - Maioria de 80%
        - Aprovação do conselho constitucional
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        if proposal.governance_level != GovernanceLevel.CONSTITUTIONAL:
            return False
        
        if proposal.decision_type != DecisionType.AMENDMENT:
            return False
        
        # Verifica se foi aprovada
        result, confidence, _ = self.calculate_governance_result(proposal_id)
        
        if result != VoteResult.APPROVED:
            return False
        
        # Verifica requisitos de quórum e maioria para emendas constitucionais
        if proposal.required_quorum < 0.75 or proposal.required_majority < 0.8:
            return False
        
        # Verifica se o conselho constitucional aprovou
        if confidence < 0.8:
            return False
        
        return True
    
    def generate_proposal_id(self, title: str, proposer: str) -> str:
        """Gera ID único para proposta"""
        import hashlib
        data = f"{title}_{proposer}_{len(self.proposals)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def generate_decision_id(self, proposal_id: str) -> str:
        """Gera ID único para decisão"""
        import hashlib
        data = f"{proposal_id}_{len(self.decisions)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_active_proposals(self) -> List[Dict]:
        """Obtém propostas ativas"""
        active = []
        for proposal in self.proposals.values():
            if proposal.status == "Pending" and proposal.expires_at > datetime.now():
                active.append({
                    "id": proposal.proposal_id,
                    "title": proposal.title,
                    "description": proposal.description,
                    "proposer": proposal.proposer,
                    "level": proposal.governance_level.value,
                    "type": proposal.decision_type.value,
                    "created_at": proposal.created_at.isoformat(),
                    "expires_at": proposal.expires_at.isoformat(),
                    "votes_count": len(proposal.votes)
                })
        return active

def main():
    """Exemplo de uso da Governança Horizontal"""
    
    governanca = GovernancaHorizontal()
    
    # Exemplo de proposta constitucional
    proposal_id = governanca.submit_proposal(
        proposer="expert_123",
        title="Emenda Constitucional: Equivalência Ética",
        description="Implementar o princípio de Equivalência Ética em todos os domínios",
        governance_level=GovernanceLevel.CONSTITUTIONAL,
        decision_type=DecisionType.AMENDMENT,
        required_quorum=0.75,
        required_majority=0.8
    )
    
    print("=== SISTEMA DE GOVERNANÇA HORIZONTAL ===")
    print(f"Proposta submetida: {proposal_id}")
    print()
    
    # Forma conselho
    council = governanca.form_governance_council(proposal_id)
    print(f"Conselho formado: {council}")
    print()
    
    # Simula votação
    votes = ["approve", "approve", "reject", "approve", "abstain"]
    for i, member in enumerate(council):
        if i < len(votes):
            governanca.cast_governance_vote(proposal_id, member, votes[i])
    
    # Calcula resultado
    result, confidence, justification = governanca.calculate_governance_result(proposal_id)
    print(f"Resultado: {result.value}")
    print(f"Confiança: {confidence:.2f}")
    print(f"Justificativa: {justification}")
    print()
    
    # Estatísticas
    stats = governanca.get_governance_statistics()
    print("=== ESTATÍSTICAS DE GOVERNANÇA ===")
    print(f"Propostas Totais: {stats['total_proposals']}")
    print(f"Propostas Ativas: {stats['active_proposals']}")
    print(f"Decisões Tomadas: {stats['total_decisions']}")
    print()
    print("Distribuição por Nível:")
    for level, count in stats['level_distribution'].items():
        print(f"  {level}: {count}")

if __name__ == "__main__":
    main()