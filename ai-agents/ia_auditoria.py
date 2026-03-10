#!/usr/bin/env python3
"""
Sistema de IA de Auditoria para Moral Money

Este agente de IA implementa o coração do sistema de auditoria baseado em:
- Equivalência Ética
- Conselho dos 5
- Governança Horizontal
- P2P Offline

Integração com blockchain Substrate via RPC
"""

import json
import requests
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContributionType(Enum):
    CONSTRUCTION = "Construction"
    AGRICULTURE = "Agriculture"
    ENERGY = "Energy"
    GOVERNANCE = "Governance"
    HEALTH = "Health"
    LOGISTICS = "Logistics"

class AuditResult(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ANOMALY_DETECTED = "AnomalyDetected"

@dataclass
class Expert:
    account_id: str
    reputation: int
    domain: ContributionType
    expertise_score: float

@dataclass
class Process:
    id: int
    creator: str
    domain: ContributionType
    description: str
    buildcoin_value: int
    participants: List[str]
    status: str
    audit_agent: Optional[str]

@dataclass
class AuditReport:
    process_id: int
    audit_result: AuditResult
    confidence_score: float
    council_members: List[str]
    justification: str
    ethical_equivalence: Dict[str, float]

class MoralMoneyIA:
    """
    Sistema de IA de Auditoria para Moral Money
    
    Implementa:
    1. Seleção automática de conselho dos 5
    2. Avaliação baseada em Equivalência Ética
    3. Análise de contribuições reais vs. capital
    4. Detecção de anomalias e fraudes
    5. Integração P2P offline
    """
    
    def __init__(self, rpc_endpoint: str = "http://localhost:9933"):
        self.rpc_endpoint = rpc_endpoint
        self.council_cache = {}
        
    def get_top_experts(self, domain: ContributionType, limit: int = 5) -> List[Expert]:
        """
        Seleciona os top 5 especialistas em um domínio específico
        
        Baseado na função select_top_experts() do pallet de reputação
        """
        try:
            # Chama a função do pallet de reputação via RPC
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_selectTopExperts",
                "params": [domain.value],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            result = response.json()
            
            experts = []
            for account_data in result['result']:
                expert = Expert(
                    account_id=account_data['account'],
                    reputation=account_data['reputation'],
                    domain=domain,
                    expertise_score=self.calculate_expertise_score(account_data['reputation'])
                )
                experts.append(expert)
                
            return experts[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao obter especialistas: {e}")
            return []
    
    def calculate_expertise_score(self, reputation: int) -> float:
        """Calcula score de expertise baseado na reputação"""
        max_rep = 1_000_000
        return min(reputation / max_rep, 1.0)
    
    def analyze_process(self, process: Process) -> Tuple[AuditResult, float, str]:
        """
        Analisa um processo e determina o resultado da auditoria
        
        Implementa a Equivalência Ética: Trabalho = Capital
        """
        # 1. Validação de domínio
        if not self.validate_domain_expertise(process.domain):
            return AuditResult.REJECTED, 0.0, "Domínio não possui especialistas suficientes"
        
        # 2. Análise de Equivalência Ética
        ethical_score, equivalence_analysis = self.analyze_ethical_equivalence(process)
        
        # 3. Verificação de anomalias
        anomaly_score, anomaly_report = self.detect_anomalies(process)
        
        # 4. Cálculo do score final
        final_score = (ethical_score * 0.7) + (anomaly_score * 0.3)
        
        # 5. Decisão
        if final_score >= 0.8:
            return AuditResult.APPROVED, final_score, f"Aprovado - Score: {final_score:.2f}"
        elif final_score >= 0.5:
            return AuditResult.ANOMALY_DETECTED, final_score, f"Anomalia detectada - Score: {final_score:.2f}"
        else:
            return AuditResult.REJECTED, final_score, f"Rejeitado - Score: {final_score:.2f}"
    
    def analyze_ethical_equivalence(self, process: Process) -> Tuple[float, Dict]:
        """
        Implementa a Equivalência Ética: Trabalho = Capital
        
        Exemplo: Investidor 60 anos, 4M€ = Trabalhador 30 anos
        """
        equivalence_analysis = {
            "capital_value": 0,
            "work_value": 0,
            "equivalence_ratio": 0,
            "ethical_score": 0
        }
        
        # Simulação de cálculo de Equivalência Ética
        # Baseado na idade, capital investido e trabalho realizado
        
        # Fatores de equivalência
        age_factor = 1.0
        capital_factor = 1.0
        work_factor = 1.0
        
        # Cálculo simplificado (na prática seria mais complexo)
        capital_equivalent = process.buildcoin_value * capital_factor
        work_equivalent = len(process.participants) * 1000 * work_factor
        
        equivalence_ratio = work_equivalent / capital_equivalent if capital_equivalent > 0 else 1.0
        
        # Score ético baseado na equivalência
        ethical_score = min(equivalence_ratio, 1.0)
        
        equivalence_analysis.update({
            "capital_value": capital_equivalent,
            "work_value": work_equivalent,
            "equivalence_ratio": equivalence_ratio,
            "ethical_score": ethical_score
        })
        
        return ethical_score, equivalence_analysis
    
    def detect_anomalies(self, process: Process) -> Tuple[float, str]:
        """
        Detecção de anomalias e possíveis fraudes
        
        Verifica:
        - Participantes suspeitos
        - Valores inconsistentes
        - Padrões de comportamento
        """
        anomaly_score = 1.0  # 1.0 = sem anomalias, 0.0 = muitas anomalias
        anomaly_report = []
        
        # Verificação de participantes
        if len(process.participants) < 2:
            anomaly_score -= 0.2
            anomaly_report.append("Número insuficiente de participantes")
        
        # Verificação de valores
        if process.buildcoin_value > 1000000:  # Valor muito alto
            anomaly_score -= 0.3
            anomaly_report.append("Valor de Buildcoin suspeitamente alto")
        
        # Verificação de histórico do criador
        creator_history_score = self.check_creator_history(process.creator)
        anomaly_score *= creator_history_score
        
        return anomaly_score, "; ".join(anomaly_report)
    
    def check_creator_history(self, creator: str) -> float:
        """Verifica histórico do criador do processo"""
        try:
            # Consulta reputação do criador
            payload = {
                "jsonrpc": "2.0",
                "method": "reputation_getReputation",
                "params": [creator],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            reputation = response.json()['result']
            
            # Score baseado na reputação
            max_rep = 1_000_000
            return min(reputation / max_rep, 1.0)
            
        except:
            return 0.5  # Score neutro se não conseguir consultar
    
    def form_council(self, domain: ContributionType) -> List[Expert]:
        """Forma o conselho dos 5 especialistas"""
        experts = self.get_top_experts(domain)
        
        if len(experts) < 5:
            logger.warning(f"Apenas {len(experts)} especialistas disponíveis para {domain}")
        
        return experts[:5]
    
    def validate_council(self, domain: ContributionType, council_members: List[str]) -> bool:
        """Valida se o conselho está composto pelos top 5"""
        top_experts = self.get_top_experts(domain)
        top_accounts = {expert.account_id for expert in top_experts}
        
        return all(member in top_accounts for member in council_members)
    
    def execute_audit(self, process_id: int) -> AuditReport:
        """
        Executa auditoria completa de um processo
        
        Fluxo:
        1. Obter processo
        2. Formar conselho
        3. Analisar processo
        4. Gerar relatório
        5. Integrar com blockchain
        """
        # 1. Obter processo
        process = self.get_process(process_id)
        if not process:
            raise ValueError(f"Processo {process_id} não encontrado")
        
        # 2. Formar conselho
        council = self.form_council(process.domain)
        council_members = [expert.account_id for expert in council]
        
        # 3. Analisar processo
        audit_result, confidence_score, justification = self.analyze_process(process)
        
        # 4. Análise de Equivalência Ética
        _, equivalence_analysis = self.analyze_ethical_equivalence(process)
        
        # 5. Gerar relatório
        report = AuditReport(
            process_id=process_id,
            audit_result=audit_result,
            confidence_score=confidence_score,
            council_members=council_members,
            justification=justification,
            ethical_equivalence=equivalence_analysis
        )
        
        # 6. Integrar com blockchain
        self.submit_audit_to_blockchain(process_id, audit_result, council_members)
        
        return report
    
    def get_process(self, process_id: int) -> Optional[Process]:
        """Obtém processo da blockchain"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "processes_getProcess",
                "params": [process_id],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            process_data = response.json()['result']
            
            return Process(
                id=process_data['id'],
                creator=process_data['creator'],
                domain=ContributionType(process_data['domain']),
                description=process_data['description'],
                buildcoin_value=process_data['buildcoin_value'],
                participants=process_data['participants'],
                status=process_data['status'],
                audit_agent=process_data.get('audit_agent')
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter processo: {e}")
            return None
    
    def submit_audit_to_blockchain(self, process_id: int, audit_result: AuditResult, council_members: List[str]):
        """Submete resultado da auditoria para o blockchain"""
        try:
            # Chama a função concluir_processo do pallet de processos
            payload = {
                "jsonrpc": "2.0",
                "method": "processes_concluirProcesso",
                "params": [process_id, audit_result.value, council_members],
                "id": 1
            }
            
            response = requests.post(self.rpc_endpoint, json=payload)
            logger.info(f"Auditoria submetida para processo {process_id}: {audit_result.value}")
            
        except Exception as e:
            logger.error(f"Erro ao submeter auditoria: {e}")
    
    def get_ethical_guidelines(self) -> Dict:
        """Retorna as diretrizes éticas do sistema"""
        return {
            "equivalence_principle": "Trabalho = Capital",
            "example": "Investidor 60 anos, 4M€ = Trabalhador 30 anos",
            "governance": "5 Conselheiros baseados em reputação por domínio",
            "transparency": "Todas as decisões auditáveis na blockchain",
            "merit_based": "Buildcoins só emitidos após validação de contribuição real"
        }

def main():
    """Exemplo de uso do sistema de IA de auditoria"""
    
    # Inicializa IA
    ia = MoralMoneyIA()
    
    # Exemplo de auditoria
    process_id = 123
    
    try:
        # Executa auditoria completa
        report = ia.execute_audit(process_id)
        
        print(f"=== RELATÓRIO DE AUDITORIA ===")
        print(f"Processo ID: {report.process_id}")
        print(f"Resultado: {report.audit_result.value}")
        print(f"Confiança: {report.confidence_score:.2f}")
        print(f"Conselho: {report.council_members}")
        print(f"Justificativa: {report.justification}")
        print(f"Equivalência Ética: {report.ethical_equivalence}")
        
        # Diretrizes éticas
        guidelines = ia.get_ethical_guidelines()
        print(f"\n=== DIRETRIZES ÉTICAS ===")
        for key, value in guidelines.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Erro na auditoria: {e}")

if __name__ == "__main__":
    main()