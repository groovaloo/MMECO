#!/usr/bin/env python3
"""
Sistema de Reputação Ativa para Moral Money

Implementa o sistema de reputação baseado em contribuição real e validação prática.
Substitui o conceito de tempo por mérito real e experiência comprovada.

Princípios:
- Reputação baseada em trabalho validado, não em tempo
- Multiplicadores de ganho baseados em reputação acumulada
- Sistema de slashing proporcional à responsabilidade assumida
- Progressão baseada em validação prática, não em títulos
"""

import hashlib
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReputationLevel(Enum):
    NOVICE = "Novice"           # 0-100 pontos
    APPRENTICE = "Apprentice"   # 101-500 pontos
    JOURNEYMAN = "Journeyman"   # 501-1000 pontos
    EXPERT = "Expert"          # 1001-2000 pontos
    MASTER = "Master"          # 2001+ pontos

class ValidationType(Enum):
    SELF_VALIDATED = "SelfValidated"
    PEER_VALIDATED = "PeerValidated"
    COUNCIL_VALIDATED = "CouncilValidated"
    AUTOMATIC_VALIDATED = "AutomaticValidated"

class WorkDomain(Enum):
    AGRICULTURE = "Agriculture"
    CONSTRUCTION = "Construction"
    ENERGY = "Energy"
    HEALTH = "Health"
    LOGISTICS = "Logistics"
    GOVERNANCE = "Governance"

@dataclass
class ValidationRecord:
    validator_id: str
    validation_type: ValidationType
    timestamp: float
    confidence: float  # 0.0 a 1.0
    comment: str

@dataclass
class WorkContribution:
    contribution_id: str
    contributor_id: str
    work_domain: WorkDomain
    work_description: str
    hours_worked: float
    skill_level: float  # 0.0 a 1.0
    resources_used: Dict[str, float]
    validation_records: List[ValidationRecord]
    reputation_gained: float
    timestamp: float

@dataclass
class ActiveReputation:
    account_id: str
    total_reputation: float
    domain_reputations: Dict[WorkDomain, float]
    last_activity: float
    validation_history: List[ValidationRecord]
    multiplier: float
    responsibility_level: float

class SistemaReputacaoAtiva:
    """
    Sistema de Reputação Ativa
    
    Características:
    - Reputação baseada em contribuição real
    - Multiplicadores baseados em reputação acumulada
    - Sistema de responsabilidade proporcional
    - Validação prática, não baseada em títulos
    """
    
    def __init__(self):
        # Armazenamento de dados
        self.reputations: Dict[str, ActiveReputation] = {}
        self.contributions: Dict[str, WorkContribution] = {}
        self.validation_queue: List[str] = []
        
        # Configurações de reputação
        self.base_reputation_gain = 10.0
        self.domain_multipliers = {
            WorkDomain.AGRICULTURE: 1.0,
            WorkDomain.CONSTRUCTION: 1.2,
            WorkDomain.ENERGY: 1.5,
            WorkDomain.HEALTH: 2.0,
            WorkDomain.LOGISTICS: 1.1,
            WorkDomain.GOVERNANCE: 1.8
        }
        
        # Multiplicadores por nível de reputação
        self.reputation_multipliers = {
            ReputationLevel.NOVICE: 1.0,
            ReputationLevel.APPRENTICE: 1.2,
            ReputationLevel.JOURNEYMAN: 1.5,
            ReputationLevel.EXPERT: 1.8,
            ReputationLevel.MASTER: 2.2
        }
        
        # Níveis de responsabilidade
        self.responsibility_levels = {
            WorkDomain.AGRICULTURE: 1.0,
            WorkDomain.CONSTRUCTION: 1.5,
            WorkDomain.ENERGY: 2.0,
            WorkDomain.HEALTH: 5.0,      # Alta responsabilidade
            WorkDomain.LOGISTICS: 1.2,
            WorkDomain.GOVERNANCE: 3.0   # Alta responsabilidade
        }
        
        logger.info("Sistema de Reputação Ativa inicializado")
    
    def get_reputation_level(self, reputation: float) -> ReputationLevel:
        """Determina o nível de reputação baseado no total"""
        if reputation >= 2001:
            return ReputationLevel.MASTER
        elif reputation >= 1001:
            return ReputationLevel.EXPERT
        elif reputation >= 501:
            return ReputationLevel.JOURNEYMAN
        elif reputation >= 101:
            return ReputationLevel.APPRENTICE
        else:
            return ReputationLevel.NOVICE
    
    def calculate_reputation_gain(self, contribution: WorkContribution) -> float:
        """Calcula ganho de reputação baseado em vários fatores"""
        # Baseado nas horas trabalhadas
        time_factor = contribution.hours_worked * 2.0
        
        # Baseado no nível de habilidade
        skill_factor = contribution.skill_level * 50.0
        
        # Baseado no domínio
        domain_factor = self.domain_multipliers[contribution.work_domain]
        
        # Baseado na qualidade da validação
        validation_factor = self._calculate_validation_factor(contribution.validation_records)
        
        # Baseado na reputação atual (para multiplicador)
        current_reputation = self.get_current_reputation(contribution.contributor_id)
        reputation_level = self.get_reputation_level(current_reputation)
        multiplier = self.reputation_multipliers[reputation_level]
        
        base_gain = (time_factor + skill_factor) * domain_factor * validation_factor
        final_gain = base_gain * multiplier
        
        return max(final_gain, 1.0)  # Mínimo de 1 ponto
    
    def _calculate_validation_factor(self, validations: List[ValidationRecord]) -> float:
        """Calcula fator de validação baseado na qualidade das validações"""
        if not validations:
            return 0.5  # Penalidade por falta de validação
        
        total_confidence = sum(v.confidence for v in validations)
        validation_count = len(validations)
        
        # Média da confiança
        avg_confidence = total_confidence / validation_count
        
        # Bônus por quantidade de validações (até 5)
        validation_bonus = min(validation_count / 5.0, 1.0) * 0.2
        
        return avg_confidence + validation_bonus
    
    def register_contribution(self, contributor_id: str, work_domain: WorkDomain,
                            work_description: str, hours_worked: float,
                            skill_level: float, resources_used: Dict[str, float]) -> str:
        """Registra uma contribuição de trabalho"""
        contribution_id = f"CONTRIB_{int(time.time())}_{contributor_id[:8]}"
        
        contribution = WorkContribution(
            contribution_id=contribution_id,
            contributor_id=contributor_id,
            work_domain=work_domain,
            work_description=work_description,
            hours_worked=hours_worked,
            skill_level=skill_level,
            resources_used=resources_used,
            validation_records=[],
            reputation_gained=0.0,
            timestamp=time.time()
        )
        
        self.contributions[contribution_id] = contribution
        
        # Atualiza reputação do contribuidor
        self._update_contributor_reputation(contribution)
        
        logger.info(f"Contribuição registrada: {contribution_id} por {contributor_id}")
        return contribution_id
    
    def validate_contribution(self, contribution_id: str, validator_id: str,
                            validation_type: ValidationType, confidence: float,
                            comment: str = "") -> bool:
        """Valida uma contribuição de trabalho"""
        if contribution_id not in self.contributions:
            return False
        
        contribution = self.contributions[contribution_id]
        
        # Verifica se o validador já validou
        if any(v.validator_id == validator_id for v in contribution.validation_records):
            return False
        
        # Limita número de validações
        if len(contribution.validation_records) >= 5:
            return False
        
        validation = ValidationRecord(
            validator_id=validator_id,
            validation_type=validation_type,
            timestamp=time.time(),
            confidence=confidence,
            comment=comment
        )
        
        contribution.validation_records.append(validation)
        
        # Recalcula reputação
        self._update_contributor_reputation(contribution)
        
        return True
    
    def _update_contributor_reputation(self, contribution: WorkContribution):
        """Atualiza a reputação do contribuidor"""
        contributor_id = contribution.contributor_id
        
        # Calcula ganho de reputação
        reputation_gain = self.calculate_reputation_gain(contribution)
        contribution.reputation_gained = reputation_gain
        
        # Atualiza reputação geral
        if contributor_id not in self.reputations:
            self.reputations[contributor_id] = ActiveReputation(
                account_id=contributor_id,
                total_reputation=0.0,
                domain_reputations={},
                last_activity=time.time(),
                validation_history=[],
                multiplier=1.0,
                responsibility_level=1.0
            )
        
        reputation = self.reputations[contributor_id]
        reputation.total_reputation += reputation_gain
        reputation.last_activity = time.time()
        
        # Atualiza reputação por domínio
        if contribution.work_domain not in reputation.domain_reputations:
            reputation.domain_reputations[contribution.work_domain] = 0.0
        
        reputation.domain_reputations[contribution.work_domain] += reputation_gain
        
        # Atualiza multiplicador baseado na reputação total
        reputation_level = self.get_reputation_level(reputation.total_reputation)
        reputation.multiplier = self.reputation_multipliers[reputation_level]
        
        # Atualiza nível de responsabilidade
        reputation.responsibility_level = self._calculate_responsibility_level(reputation)
    
    def _calculate_responsibility_level(self, reputation: ActiveReputation) -> float:
        """Calcula nível de responsabilidade baseado na reputação e domínios"""
        base_responsibility = 1.0
        
        # Aumenta responsabilidade por domínios de alta responsabilidade
        for domain, rep in reputation.domain_reputations.items():
            if rep > 100:  # Só conta domínios com reputação significativa
                base_responsibility += self.responsibility_levels[domain] * 0.1
        
        # Aumenta responsabilidade por reputação total alta
        if reputation.total_reputation > 1000:
            base_responsibility *= 1.5
        
        return base_responsibility
    
    def apply_slashing(self, account_id: str, error_severity: float, 
                      error_type: str = "negligence") -> bool:
        """Aplica penalização de reputação por erros graves"""
        if account_id not in self.reputations:
            return False
        
        reputation = self.reputations[account_id]
        
        # Calcula penalização baseada na responsabilidade
        base_penalty = error_severity * 50.0
        responsibility_multiplier = reputation.responsibility_level
        reputation_factor = min(reputation.total_reputation / 1000, 3.0)
        
        total_penalty = base_penalty * responsibility_multiplier * reputation_factor
        
        # Não pode zerar a reputação
        new_reputation = max(0.0, reputation.total_reputation - total_penalty)
        
        # Atualiza reputação
        reputation.total_reputation = new_reputation
        reputation.last_activity = time.time()
        
        # Registra penalização no histórico
        penalty_record = ValidationRecord(
            validator_id="SYSTEM",
            validation_type=ValidationType.AUTOMATIC_VALIDATED,
            timestamp=time.time(),
            confidence=1.0,
            comment=f"PENALTY: {error_type} - Severity: {error_severity} - Penalty: {total_penalty}"
        )
        reputation.validation_history.append(penalty_record)
        
        logger.info(f"Penalização aplicada: {account_id} - {total_penalty:.2f} pontos")
        return True
    
    def get_current_reputation(self, account_id: str) -> float:
        """Obtém reputação atual de um contribuidor"""
        if account_id in self.reputations:
            return self.reputations[account_id].total_reputation
        return 0.0
    
    def get_reputation_multiplier(self, account_id: str) -> float:
        """Obtém multiplicador de ganho baseado na reputação"""
        if account_id in self.reputations:
            return self.reputations[account_id].multiplier
        return 1.0
    
    def get_responsibility_level(self, account_id: str) -> float:
        """Obtém nível de responsabilidade"""
        if account_id in self.reputations:
            return self.reputations[account_id].responsibility_level
        return 1.0
    
    def get_domain_expertise(self, account_id: str, domain: WorkDomain) -> float:
        """Obtém expertise em um domínio específico"""
        if account_id in self.reputations:
            return self.reputations[account_id].domain_reputations.get(domain, 0.0)
        return 0.0
    
    def get_reputation_statistics(self) -> Dict:
        """Obtém estatísticas do sistema de reputação"""
        total_contributors = len(self.reputations)
        total_contributions = len(self.contributions)
        
        # Distribuição por nível
        level_counts = {level.value: 0 for level in ReputationLevel}
        for reputation in self.reputations.values():
            level = self.get_reputation_level(reputation.total_reputation)
            level_counts[level.value] += 1
        
        # Distribuição por domínio
        domain_counts = {domain.value: 0 for domain in WorkDomain}
        for contribution in self.contributions.values():
            domain_counts[contribution.work_domain.value] += 1
        
        # Média de reputação
        avg_reputation = 0.0
        if total_contributors > 0:
            avg_reputation = sum(r.total_reputation for r in self.reputations.values()) / total_contributors
        
        return {
            "total_contributors": total_contributors,
            "total_contributions": total_contributions,
            "average_reputation": avg_reputation,
            "level_distribution": level_counts,
            "domain_distribution": domain_counts,
            "highest_reputation": max((r.total_reputation for r in self.reputations.values()), default=0.0)
        }
    
    def decay_inactive_reputation(self, days_inactive: int = 90) -> int:
        """Aplica decaimento de reputação para contribuidores inativos"""
        cutoff_time = time.time() - (days_inactive * 24 * 3600)
        decayed_count = 0
        
        for reputation in self.reputations.values():
            if reputation.last_activity < cutoff_time:
                # Decaimento de 10% para inativos
                reputation.total_reputation *= 0.9
                reputation.last_activity = time.time()
                decayed_count += 1
        
        logger.info(f"Decaimento aplicado a {decayed_count} contribuidores inativos")
        return decayed_count

def main():
    """Exemplo de uso do Sistema de Reputação Ativa"""
    
    sistema = SistemaReputacaoAtiva()
    
    print("=== SISTEMA DE REPUTAÇÃO ATIVA ===")
    print()
    
    # 1. Registro de contribuições
    print("1. Registrando contribuições...")
    
    # Agricultor experiente
    contrib1 = sistema.register_contribution(
        contributor_id="agricultor_veterano",
        work_domain=WorkDomain.AGRICULTURE,
        work_description="Plantio de 100 árvores frutíferas",
        hours_worked=80.0,
        skill_level=0.9,
        resources_used={"sementes": 5.0, "fertilizante": 2.0}
    )
    print(f"   Contribuição 1: {contrib1}")
    
    # Médico recém-chegado
    contrib2 = sistema.register_contribution(
        contributor_id="medico_novato",
        work_domain=WorkDomain.HEALTH,
        work_description="Atendimento básico em clínica comunitária",
        hours_worked=40.0,
        skill_level=0.7,
        resources_used={"medicamentos": 10.0, "equipamentos": 5.0}
    )
    print(f"   Contribuição 2: {contrib2}")
    
    print()
    
    # 2. Validação das contribuições
    print("2. Validando contribuições...")
    
    # Validação do agricultor (por conselho)
    sistema.validate_contribution(
        contrib1, "conselho_agricultura", ValidationType.COUNCIL_VALIDATED, 0.9, "Excelente trabalho"
    )
    sistema.validate_contribution(
        contrib1, "vizinho1", ValidationType.PEER_VALIDATED, 0.8, "Trabalho reconhecido"
    )
    
    # Validação do médico (por conselho médico)
    sistema.validate_contribution(
        contrib2, "conselho_medico", ValidationType.COUNCIL_VALIDATED, 0.7, "Bom atendimento inicial"
    )
    
    print("   Contribuições validadas")
    print()
    
    # 3. Verificação de reputação
    print("3. Verificando reputação...")
    
    rep_agricultor = sistema.get_current_reputation("agricultor_veterano")
    rep_medico = sistema.get_current_reputation("medico_novato")
    
    mult_agricultor = sistema.get_reputation_multiplier("agricultor_veterano")
    mult_medico = sistema.get_reputation_multiplier("medico_novato")
    
    resp_agricultor = sistema.get_responsibility_level("agricultor_veterano")
    resp_medico = sistema.get_responsibility_level("medico_novato")
    
    print(f"   Agricultor - Reputação: {rep_agricultor:.2f}, Multiplicador: {mult_agricultor:.2f}, Responsabilidade: {resp_agricultor:.2f}")
    print(f"   Médico - Reputação: {rep_medico:.2f}, Multiplicador: {mult_medico:.2f}, Responsabilidade: {resp_medico:.2f}")
    print()
    
    # 4. Simulação de penalização
    print("4. Simulando penalização por erro médico...")
    sistema.apply_slashing("medico_novato", 3.0, "negligencia_leve")
    
    rep_medico_nova = sistema.get_current_reputation("medico_novato")
    print(f"   Médico após penalização: {rep_medico_nova:.2f}")
    print()
    
    # 5. Estatísticas
    print("5. Estatísticas do sistema...")
    stats = sistema.get_reputation_statistics()
    
    print(f"   Contribuidores: {stats['total_contributors']}")
    print(f"   Contribuições: {stats['total_contributions']}")
    print(f"   Média de reputação: {stats['average_reputation']:.2f}")
    print(f"   Distribuição por nível: {stats['level_distribution']}")
    print()
    
    print("=== SISTEMA DE REPUTAÇÃO ATIVA OPERACIONAL ===")
    print("Pronto para validar contribuições reais e gerenciar reputação!")

if __name__ == "__main__":
    main()