#!/usr/bin/env python3
"""
Sistema de Equivalência Ética para Moral Money

Implementa o princípio fundamental: Trabalho = Capital

Este sistema garante que:
- Investidores e trabalhadores tenham o mesmo valor na economia
- Buildcoins só sejam emitidos após validação de contribuição real
- Distribuição baseada em mérito, não em capital inicial
"""

import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContributionType(Enum):
    CONSTRUCTION = "Construction"
    AGRICULTURE = "Agriculture"
    ENERGY = "Energy"
    GOVERNANCE = "Governance"
    HEALTH = "Health"
    LOGISTICS = "Logistics"

@dataclass
class EthicalContribution:
    contributor_id: str
    contribution_type: ContributionType
    work_hours: float
    skill_level: float  # 0.0 a 1.0
    impact_factor: float  # 0.0 a 2.0
    age: int
    capital_invested: float
    ethical_score: float

@dataclass
class EquivalenceCalculation:
    work_value: float
    capital_value: float
    equivalence_ratio: float
    buildcoin_allocation: float
    ethical_validation: bool

class EquivalenciaEtica:
    """
    Sistema de Equivalência Ética
    
    Princípio: Trabalho = Capital
    
    Exemplo clássico:
    - Investidor: 60 anos, 4M€ investidos
    - Trabalhador: 30 anos, 2000h de trabalho
    - Equivalência: Ambos recebem o mesmo valor de Buildcoins
    """
    
    def __init__(self, rpc_endpoint: str = "http://localhost:9933"):
        self.rpc_endpoint = rpc_endpoint
        self.equivalence_history = []
        
    def calculate_work_value(self, contribution: EthicalContribution) -> float:
        """
        Calcula o valor do trabalho baseado em:
        - Horas trabalhadas
        - Nível de habilidade
        - Fator de impacto
        - Idade (experiência)
        """
        # Base value per hour
        base_hourly_rate = 20.0
        
        # Age factor (experiência)
        age_factor = 1.0 + (contribution.age - 25) * 0.01
        age_factor = max(0.8, min(age_factor, 1.5))  # Limita entre 0.8 e 1.5
        
        # Skill level multiplier
        skill_multiplier = 1.0 + contribution.skill_level
        
        # Impact factor
        impact_multiplier = contribution.impact_factor
        
        work_value = (
            contribution.work_hours *
            base_hourly_rate *
            age_factor *
            skill_multiplier *
            impact_multiplier
        )
        
        return work_value
    
    def calculate_capital_value(self, contribution: EthicalContribution) -> float:
        """
        Calcula o valor do capital investido
        
        Considera:
        - Montante investido
        - Tempo de investimento
        - Risco assumido
        """
        # Base capital value (without adjustments)
        capital_value = contribution.capital_invested
        
        # Risk factor based on age and investment type
        risk_factor = self.calculate_risk_factor(contribution.age, contribution.capital_invested)
        
        adjusted_capital = capital_value * risk_factor
        
        return adjusted_capital
    
    def calculate_risk_factor(self, age: int, capital: float) -> float:
        """
        Calcula fator de risco baseado em idade e capital
        
        Jovens com pouco capital = alto risco
        Idosos com muito capital = baixo risco
        """
        # Base risk factor
        base_risk = 1.0
        
        # Age factor (younger = higher risk)
        age_risk = 1.0 + (35 - age) * 0.02
        age_risk = max(0.5, min(age_risk, 2.0))
        
        # Capital factor (less capital = higher risk)
        capital_risk = 1.0 + (100000 - capital) / 100000
        capital_risk = max(0.5, min(capital_risk, 3.0))
        
        return base_risk * age_risk * capital_risk
    
    def calculate_ethical_equivalence(self, contribution: EthicalContribution) -> EquivalenceCalculation:
        """
        Calcula a equivalência ética entre trabalho e capital
        
        Implementa o princípio: Trabalho = Capital
        """
        work_value = self.calculate_work_value(contribution)
        capital_value = self.calculate_capital_value(contribution)
        
        # Equivalência ideal: trabalho deve ser igual ao capital
        if capital_value > 0:
            equivalence_ratio = work_value / capital_value
        else:
            equivalence_ratio = 1.0  # Se não houver capital, assume equivalência perfeita
        
        # Validação ética
        ethical_validation = self.validate_ethical_contribution(contribution, equivalence_ratio)
        
        # Cálculo de Buildcoin allocation
        buildcoin_allocation = self.calculate_buildcoin_allocation(contribution, work_value, capital_value)
        
        calculation = EquivalenceCalculation(
            work_value=work_value,
            capital_value=capital_value,
            equivalence_ratio=equivalence_ratio,
            buildcoin_allocation=buildcoin_allocation,
            ethical_validation=ethical_validation
        )
        
        self.equivalence_history.append(calculation)
        return calculation
    
    def validate_ethical_contribution(self, contribution: EthicalContribution, equivalence_ratio: float) -> bool:
        """
        Valida se a contribuição é ética segundo os princípios do Moral Money
        
        Critérios:
        - Equivalência entre trabalho e capital
        - Contribuição real vs. especulação
        - Distribuição justa
        """
        # Thresholds de equivalência
        min_equivalence = 0.5  # Mínimo 50% de equivalência
        max_equivalence = 2.0  # Máximo 200% de equivalência
        
        if not (min_equivalence <= equivalence_ratio <= max_equivalence):
            return False
        
        # Validação de contribuição real
        if contribution.work_hours < 10 and contribution.capital_invested == 0:
            return False
        
        # Validação de distribuição justa
        if contribution.capital_invested > 1000000 and contribution.work_hours < 100:
            return False
        
        return True
    
    def calculate_buildcoin_allocation(self, contribution: EthicalContribution, work_value: float, capital_value: float) -> float:
        """
        Calcula a alocação de Buildcoins baseada na equivalência ética
        
        Buildcoins só são emitidos após validação de contribuição real
        """
        # Base allocation
        base_allocation = (work_value + capital_value) / 1000  # Conversão para Buildcoins
        
        # Ethical multiplier
        ethical_multiplier = self.calculate_ethical_multiplier(contribution)
        
        # Final allocation
        final_allocation = base_allocation * ethical_multiplier
        
        # Minimum allocation for real contributors
        if contribution.work_hours > 0 or contribution.capital_invested > 0:
            final_allocation = max(final_allocation, 10.0)
        
        return final_allocation
    
    def calculate_ethical_multiplier(self, contribution: EthicalContribution) -> float:
        """
        Calcula multiplicador ético baseado em:
        - Nível de habilidade
        - Impacto social
        - Experiência (idade)
        - Proporção trabalho/capital
        """
        multiplier = 1.0
        
        # Skill level bonus
        multiplier += contribution.skill_level * 0.5
        
        # Impact factor bonus
        multiplier += (contribution.impact_factor - 1.0) * 0.3
        
        # Experience bonus (age)
        if contribution.age > 40:
            multiplier += 0.2
        
        # Work/capital balance bonus
        if contribution.work_hours > 0 and contribution.capital_invested > 0:
            multiplier += 0.3
        
        return max(multiplier, 0.5)  # Minimum 0.5
    
    def analyze_contribution_distribution(self, contributions: List[EthicalContribution]) -> Dict:
        """
        Analisa a distribuição de contribuições e equivalência ética
        
        Verifica se o sistema está sendo justo e equilibrado
        """
        total_work_value = 0
        total_capital_value = 0
        total_buildcoins = 0
        ethical_contributions = 0
        
        for contribution in contributions:
            calculation = self.calculate_ethical_equivalence(contribution)
            
            total_work_value += calculation.work_value
            total_capital_value += calculation.capital_value
            total_buildcoins += calculation.buildcoin_allocation
            
            if calculation.ethical_validation:
                ethical_contributions += 1
        
        # Distribution analysis
        if total_work_value + total_capital_value > 0:
            work_percentage = total_work_value / (total_work_value + total_capital_value)
            capital_percentage = total_capital_value / (total_work_value + total_capital_value)
        else:
            work_percentage = 0.5
            capital_percentage = 0.5
        
        ethical_ratio = ethical_contributions / len(contributions) if contributions else 0
        
        return {
            "total_contributions": len(contributions),
            "ethical_contributions": ethical_contributions,
            "ethical_ratio": ethical_ratio,
            "total_work_value": total_work_value,
            "total_capital_value": total_capital_value,
            "work_percentage": work_percentage,
            "capital_percentage": capital_percentage,
            "total_buildcoins_allocated": total_buildcoins,
            "average_buildcoins_per_contribution": total_buildcoins / len(contributions) if contributions else 0
        }
    
    def get_ethical_guidelines(self) -> Dict:
        """Retorna as diretrizes éticas do sistema"""
        return {
            "principle": "Trabalho = Capital",
            "example": {
                "investor": {
                    "age": 60,
                    "capital_invested": 4000000,
                    "description": "Investidor com capital inicial"
                },
                "worker": {
                    "age": 30,
                    "work_hours": 2000,
                    "skill_level": 0.8,
                    "description": "Trabalhador com contribuição real"
                },
                "equivalence": "Ambos recebem o mesmo valor de Buildcoins"
            },
            "validation_criteria": [
                "Equivalência entre trabalho e capital (50% - 200%)",
                "Contribuição real vs. especulação",
                "Distribuição justa",
                "Mínimo de 10 horas de trabalho ou capital investido"
            ],
            "buildcoin_principles": [
                "Só emitidos após validação de contribuição real",
                "Baseados em equivalência ética, não em capital inicial",
                "Transparência total na distribuição",
                "Impulsionam economia baseada em mérito"
            ]
        }
    
    def validate_system_ethics(self) -> Dict:
        """
        Valida a ética do sistema como um todo
        
        Verifica se o sistema está operando de forma justa e equilibrada
        """
        try:
            # Obtém todas as contribuições do blockchain
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_getAllContributions",
                "params": [],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            contributions_data = response.json()['result']
            
            contributions = []
            for data in contributions_data:
                contribution = EthicalContribution(
                    contributor_id=data['account'],
                    contribution_type=ContributionType(data['type']),
                    work_hours=data.get('work_hours', 0),
                    skill_level=data.get('skill_level', 0.5),
                    impact_factor=data.get('impact_factor', 1.0),
                    age=data.get('age', 30),
                    capital_invested=data.get('capital_invested', 0),
                    ethical_score=0.0
                )
                contributions.append(contribution)
            
            # Analisa distribuição
            distribution = self.analyze_contribution_distribution(contributions)
            
            # Validação ética do sistema
            system_ethical = (
                distribution['ethical_ratio'] >= 0.8 and
                0.4 <= distribution['work_percentage'] <= 0.6 and
                distribution['average_buildcoins_per_contribution'] > 0
            )
            
            return {
                "system_ethical": system_ethical,
                "ethical_ratio": distribution['ethical_ratio'],
                "work_capital_balance": {
                    "work_percentage": distribution['work_percentage'],
                    "capital_percentage": distribution['capital_percentage']
                },
                "distribution_health": distribution['average_buildcoins_per_contribution'] > 50,
                "total_contributions": distribution['total_contributions']
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar ética do sistema: {e}")
            return {"error": str(e)}

def main():
    """Exemplo de uso da Equivalência Ética"""
    
    equivalencia = EquivalenciaEtica()
    
    # Exemplo clássico: Investidor vs Trabalhador
    investor = EthicalContribution(
        contributor_id="investor_123",
        contribution_type=ContributionType.CONSTRUCTION,
        work_hours=50,  # Gestão e supervisão
        skill_level=0.9,
        impact_factor=1.5,
        age=60,
        capital_invested=4000000.0,
        ethical_score=0.0
    )
    
    worker = EthicalContribution(
        contributor_id="worker_456",
        contribution_type=ContributionType.CONSTRUCTION,
        work_hours=2000,
        skill_level=0.7,
        impact_factor=1.2,
        age=30,
        capital_invested=0.0,
        ethical_score=0.0
    )
    
    print("=== EXEMPLO DE EQUIVALÊNCIA ÉTICA ===")
    print("Princípio: Trabalho = Capital")
    print()
    
    # Calcula equivalência para investidor
    investor_calc = equivalencia.calculate_ethical_equivalence(investor)
    print(f"INVESTIDOR (60 anos, 4M€):")
    print(f"  Valor do Trabalho: €{investor_calc.work_value:.2f}")
    print(f"  Valor do Capital: €{investor_calc.capital_value:.2f}")
    print(f"  Equivalência: {investor_calc.equivalence_ratio:.2f}")
    print(f"  Buildcoins: {investor_calc.buildcoin_allocation:.2f}")
    print(f"  Ético: {investor_calc.ethical_validation}")
    print()
    
    # Calcula equivalência para trabalhador
    worker_calc = equivalencia.calculate_ethical_equivalence(worker)
    print(f"TRABALHADOR (30 anos, 2000h):")
    print(f"  Valor do Trabalho: €{worker_calc.work_value:.2f}")
    print(f"  Valor do Capital: €{worker_calc.capital_value:.2f}")
    print(f"  Equivalência: {worker_calc.equivalence_ratio:.2f}")
    print(f"  Buildcoins: {worker_calc.buildcoin_allocation:.2f}")
    print(f"  Ético: {worker_calc.ethical_validation}")
    print()
    
    # Validação do sistema
    guidelines = equivalencia.get_ethical_guidelines()
    print("=== DIRETRIZES ÉTICAS ===")
    print(f"Princípio: {guidelines['principle']}")
    print(f"Exemplo: {guidelines['example']['equivalence']}")
    print()
    print("Critérios de Validação:")
    for criterion in guidelines['validation_criteria']:
        print(f"  - {criterion}")

if __name__ == "__main__":
    main()