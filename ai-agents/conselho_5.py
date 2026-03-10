#!/usr/bin/env python3
"""
Sistema de Conselho dos 5 para Moral Money

Implementa o sistema de governança horizontal baseado em reputação por domínio.
O conselho dos 5 é soberano e suas decisões são finais e imutáveis.

Funcionalidades:
- Seleção automática de conselheiros
- Votação baseada em reputação
- Resolução de conflitos
- Integração com IA de auditoria
"""

import json
import requests
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Vote(Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
    ABSTAIN = "Abstain"

class CouncilDecision(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CONFLICT = "Conflict"
    INVALID = "Invalid"

@dataclass
class CouncilMember:
    account_id: str
    reputation: int
    domain: str
    vote_weight: float
    expertise_score: float

@dataclass
class CouncilSession:
    session_id: str
    process_id: int
    domain: str
    members: List[CouncilMember]
    votes: Dict[str, Vote]
    decision: Optional[CouncilDecision]
    confidence: float

class ConselhoDos5:
    """
    Sistema de Conselho dos 5 para Governança Horizontal
    
    Princípios:
    1. Baseado em reputação por domínio
    2. Decisões soberanas e finais
    3. Transparência total
    4. Imparcialidade garantida
    """
    
    def __init__(self, rpc_endpoint: str = "http://localhost:9933"):
        self.rpc_endpoint = rpc_endpoint
        self.sessions = {}
        
    def select_council(self, domain: str, process_id: int) -> List[CouncilMember]:
        """
        Seleciona os 5 conselheiros com maior reputação no domínio
        
        Baseado na reputação acumulada em contribuições específicas
        """
        try:
            # Obtém top 5 especialistas do domínio
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_selectTopExperts",
                "params": [domain],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            experts_data = response.json()['result']
            
            council_members = []
            for i, expert_data in enumerate(experts_data):
                member = CouncilMember(
                    account_id=expert_data['account'],
                    reputation=expert_data['reputation'],
                    domain=domain,
                    vote_weight=self.calculate_vote_weight(expert_data['reputation']),
                    expertise_score=self.calculate_expertise_score(expert_data['reputation'])
                )
                council_members.append(member)
                
            return council_members[:5]
            
        except Exception as e:
            logger.error(f"Erro ao selecionar conselho: {e}")
            return []
    
    def calculate_vote_weight(self, reputation: int) -> float:
        """Calcula peso do voto baseado na reputação"""
        max_rep = 1_000_000
        base_weight = reputation / max_rep
        
        # Ajuste exponencial para maior diferenciação
        return min(base_weight ** 0.5, 1.0)
    
    def calculate_expertise_score(self, reputation: int) -> float:
        """Calcula score de expertise"""
        max_rep = 1_000_000
        return min(reputation / max_rep, 1.0)
    
    def validate_council(self, domain: str, council_members: List[str]) -> bool:
        """Valida se o conselho está composto pelos top 5"""
        top_experts = self.select_council(domain, 0)
        top_accounts = {member.account_id for member in top_experts}
        
        return all(member in top_accounts for member in council_members)
    
    def start_session(self, process_id: int, domain: str) -> CouncilSession:
        """Inicia uma sessão de conselho"""
        council_members = self.select_council(domain, process_id)
        
        if len(council_members) < 3:
            raise ValueError("Número insuficiente de conselheiros")
        
        session_id = self.generate_session_id(process_id, domain)
        
        session = CouncilSession(
            session_id=session_id,
            process_id=process_id,
            domain=domain,
            members=council_members,
            votes={},
            decision=None,
            confidence=0.0
        )
        
        self.sessions[session_id] = session
        logger.info(f"Sessão iniciada: {session_id} para processo {process_id}")
        
        return session
    
    def cast_vote(self, session_id: str, member_id: str, vote: Vote) -> bool:
        """Registra voto de um conselheiro"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Verifica se o membro pertence ao conselho
        if not any(member.account_id == member_id for member in session.members):
            return False
        
        # Verifica se já votou
        if member_id in session.votes:
            return False
        
        session.votes[member_id] = vote
        logger.info(f"Voto registrado: {member_id} -> {vote.value}")
        
        return True
    
    def calculate_decision(self, session_id: str) -> Tuple[CouncilDecision, float]:
        """Calcula decisão do conselho baseado nos votos"""
        if session_id not in self.sessions:
            return CouncilDecision.INVALID, 0.0
        
        session = self.sessions[session_id]
        
        # Verifica se todos os membros votaram
        if len(session.votes) < len(session.members):
            return CouncilDecision.INVALID, 0.0
        
        # Calcula votos ponderados
        approve_weight = 0.0
        reject_weight = 0.0
        abstain_weight = 0.0
        
        for member_id, vote in session.votes.items():
            member = next(m for m in session.members if m.account_id == member_id)
            weight = member.vote_weight
            
            if vote == Vote.APPROVE:
                approve_weight += weight
            elif vote == Vote.REJECT:
                reject_weight += weight
            elif vote == Vote.ABSTAIN:
                abstain_weight += weight
        
        total_weight = approve_weight + reject_weight + abstain_weight
        
        if total_weight == 0:
            return CouncilDecision.INVALID, 0.0
        
        # Decisão majoritária ponderada
        approve_ratio = approve_weight / total_weight
        reject_ratio = reject_weight / total_weight
        
        # Thresholds de decisão
        if approve_ratio >= 0.6:
            decision = CouncilDecision.APPROVED
            confidence = approve_ratio
        elif reject_ratio >= 0.6:
            decision = CouncilDecision.REJECTED
            confidence = reject_ratio
        else:
            decision = CouncilDecision.CONFLICT
            confidence = max(approve_ratio, reject_ratio)
        
        session.decision = decision
        session.confidence = confidence
        
        return decision, confidence
    
    def resolve_conflict(self, process_id: int, domain: str) -> CouncilDecision:
        """
        Resolve conflitos através de nova votação do conselho
        
        Em caso de empate ou decisão CONFLICT, o conselho pode:
        1. Reavaliar o caso
        2. Solicitar mais informações
        3. Tomar decisão soberana baseada na reputação
        """
        session = self.start_session(process_id, domain)
        
        # Em caso de conflito, decisão baseada na reputação dos membros
        total_reputation = sum(member.reputation for member in session.members)
        
        if total_reputation == 0:
            return CouncilDecision.INVALID
        
        # Ponderação por reputação
        approve_reputation = 0
        reject_reputation = 0
        
        for member in session.members:
            # Simulação de decisão baseada em reputação
            if member.expertise_score > 0.7:  # Especialistas senior
                approve_reputation += member.reputation
            else:
                reject_reputation += member.reputation
        
        approve_ratio = approve_reputation / total_reputation
        
        if approve_ratio >= 0.55:
            return CouncilDecision.APPROVED
        else:
            return CouncilDecision.REJECTED
    
    def get_council_statistics(self, domain: str) -> Dict:
        """Obtém estatísticas do conselho por domínio"""
        try:
            council = self.select_council(domain, 0)
            
            total_reputation = sum(member.reputation for member in council)
            avg_reputation = total_reputation / len(council) if council else 0
            max_reputation = max(member.reputation for member in council) if council else 0
            
            return {
                "domain": domain,
                "total_members": len(council),
                "total_reputation": total_reputation,
                "average_reputation": avg_reputation,
                "max_reputation": max_reputation,
                "members": [
                    {
                        "account": member.account_id,
                        "reputation": member.reputation,
                        "expertise_score": member.expertise_score
                    }
                    for member in council
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def generate_session_id(self, process_id: int, domain: str) -> str:
        """Gera ID único para sessão"""
        import hashlib
        data = f"{process_id}_{domain}_{len(self.sessions)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_session_status(self, session_id: str) -> Dict:
        """Obtém status de uma sessão"""
        if session_id not in self.sessions:
            return {"error": "Sessão não encontrada"}
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session.session_id,
            "process_id": session.process_id,
            "domain": session.domain,
            "members_count": len(session.members),
            "votes_count": len(session.votes),
            "decision": session.decision.value if session.decision else None,
            "confidence": session.confidence,
            "votes": {k: v.value for k, v in session.votes.items()}
        }
    
    def validate_decision_immutability(self, process_id: int) -> bool:
        """
        Valida a imutabilidade das decisões do conselho
        
        As decisões do conselho dos 5 são soberanas e não podem ser alteradas
        """
        try:
            # Verifica se o processo já foi decidido
            payload = {
                "jsonrpc": "2.0",
                "method": "processes_getProcess",
                "params": [process_id],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            process_data = response.json()['result']
            
            # Se o processo já foi concluído, a decisão é imutável
            return process_data['status'] in ['Completed', 'Conflict', 'CompletedImmutable']
            
        except Exception as e:
            logger.error(f"Erro ao validar imutabilidade: {e}")
            return False

def main():
    """Exemplo de uso do Conselho dos 5"""
    
    conselho = ConselhoDos5()
    
    # Exemplo de processo
    process_id = 456
    domain = "Construction"
    
    try:
        # Inicia sessão
        session = conselho.start_session(process_id, domain)
        print(f"=== SESSÃO DO CONSELHO DOS 5 ===")
        print(f"Processo: {process_id}")
        print(f"Domínio: {domain}")
        print(f"Membros: {[m.account_id for m in session.members]}")
        
        # Simula votação
        votes = [Vote.APPROVE, Vote.APPROVE, Vote.REJECT, Vote.APPROVE, Vote.ABSTAIN]
        for i, member in enumerate(session.members):
            if i < len(votes):
                conselho.cast_vote(session.session_id, member.account_id, votes[i])
        
        # Calcula decisão
        decision, confidence = conselho.calculate_decision(session.session_id)
        print(f"\nDecisão: {decision.value}")
        print(f"Confiança: {confidence:.2f}")
        
        # Estatísticas
        stats = conselho.get_council_statistics(domain)
        print(f"\n=== ESTATÍSTICAS DO CONSELHO ===")
        print(f"Membros: {stats.get('total_members', 0)}")
        print(f"Reputação Média: {stats.get('average_reputation', 0):.0f}")
        
    except Exception as e:
        logger.error(f"Erro no conselho: {e}")

if __name__ == "__main__":
    main()