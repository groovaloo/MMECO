#!/usr/bin/env python3
"""
Sistema Territorial para Moral Money

Implementa o lastro territorial da Buildcoin baseado em desenvolvimento físico.
Sistema de valoração de território sem vigilância constante.

Princípios:
- 1 Buildcoin = 1m² de território desenvolvido
- Valoração baseada em provas de desenvolvimento
- Auditoria por consenso, não por vigilância
- Privacidade total dos indivíduos
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

class DevelopmentLevel(Enum):
    RAW = "Raw"           # Terreno bruto - 0.5 Buildcoins/m²
    BASIC = "Basic"       # Infraestrutura básica - 1.0 Buildcoins/m²
    DEVELOPED = "Developed"  # Edificações - 2.0 Buildcoins/m²
    ADVANCED = "Advanced"    # Desenvolvimento avançado - 3.0+ Buildcoins/m²

class ProcessStatus(Enum):
    OPEN = "Open"
    VALIDATING = "Validating"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CONTESTED = "Contested"

@dataclass
class GeoLocation:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    
    def to_hash(self) -> str:
        """Converte localização geográfica para hash"""
        data = f"{self.latitude}_{self.longitude}_{self.altitude or 0}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

@dataclass
class ProofRecord:
    proof_hash: str
    timestamp: float
    geolocation: GeoLocation
    description: str
    validator_signature: Optional[str] = None

@dataclass
class TerritorialProcess:
    process_id: str
    m2_id: str
    geolocation: GeoLocation
    start_proof: ProofRecord
    end_proof: Optional[ProofRecord]
    resources_used: Dict[str, float]
    time_spent: float
    validator_votes: List[str]
    status: ProcessStatus
    created_at: float
    last_updated: float

@dataclass
class TerritorialAsset:
    m2_id: str
    geolocation: GeoLocation
    development_level: DevelopmentLevel
    last_valuation: float
    current_value: float
    owner: str
    validation_history: List[str]

class SistemaTerritorial:
    """
    Sistema de Valoração Territorial
    
    Características:
    - Lastro físico da Buildcoin
    - Auditoria por provas, não por vigilância
    - Validação por consenso comunitário
    - Privacidade total dos indivíduos
    """
    
    def __init__(self):
        # Armazenamento de dados
        self.processes: Dict[str, TerritorialProcess] = {}
        self.assets: Dict[str, TerritorialAsset] = {}
        self.proof_registry: Dict[str, ProofRecord] = {}
        
        # Configurações
        self.contestation_period = 14 * 24 * 3600  # 14 dias em segundos
        self.validation_radius = 500  # 500 metros para validação por vizinhos
        self.minimum_construction_time = 7 * 24 * 3600  # 7 dias mínimo
        
        # VALORES DE REALISMO - Versão 1.0 Caldas da Rainha
        # 1 Buildcoin = 1,00 € (lastro real)
        # Valor inicial do m² rústico na Serra do Bouro: 1,00 Buildcoin
        self.development_values = {
            DevelopmentLevel.RAW: 1.0,      # Terreno bruto - 1,00 Buildcoin/m² (1€)
            DevelopmentLevel.BASIC: 2.0,    # Infraestrutura básica - 2,00 Buildcoins/m² (2€)
            DevelopmentLevel.DEVELOPED: 4.0, # Edificações - 4,00 Buildcoins/m² (4€)
            DevelopmentLevel.ADVANCED: 6.0  # Desenvolvimento avançado - 6,00 Buildcoins/m² (6€)
        }
        
        logger.info("Sistema Territorial inicializado")
    
    def create_m2_id(self, geolocation: GeoLocation) -> str:
        """Cria ID único para m² baseado na localização"""
        return f"M2_{geolocation.to_hash()}"
    
    def register_start_proof(self, geolocation: GeoLocation, description: str) -> str:
        """Registra prova de início de desenvolvimento"""
        proof_hash = self._create_proof_hash(geolocation, description, "start")
        
        proof = ProofRecord(
            proof_hash=proof_hash,
            timestamp=time.time(),
            geolocation=geolocation,
            description=description
        )
        
        self.proof_registry[proof_hash] = proof
        
        # Cria processo territorial
        m2_id = self.create_m2_id(geolocation)
        process_id = f"PROC_{proof_hash[:12]}"
        
        process = TerritorialProcess(
            process_id=process_id,
            m2_id=m2_id,
            geolocation=geolocation,
            start_proof=proof,
            end_proof=None,
            resources_used={},
            time_spent=0,
            validator_votes=[],
            status=ProcessStatus.OPEN,
            created_at=time.time(),
            last_updated=time.time()
        )
        
        self.processes[process_id] = process
        
        # Cria asset se não existir
        if m2_id not in self.assets:
            asset = TerritorialAsset(
                m2_id=m2_id,
                geolocation=geolocation,
                development_level=DevelopmentLevel.RAW,
                last_valuation=time.time(),
                current_value=0.5,
                owner="",
                validation_history=[]
            )
            self.assets[m2_id] = asset
        
        logger.info(f"Prova de início registrada: {process_id}")
        return process_id
    
    def register_end_proof(self, process_id: str, description: str) -> bool:
        """Registra prova de conclusão de desenvolvimento"""
        if process_id not in self.processes:
            logger.error(f"Processo não encontrado: {process_id}")
            return False
        
        process = self.processes[process_id]
        
        # Verifica tempo mínimo de construção
        time_elapsed = time.time() - process.start_proof.timestamp
        if time_elapsed < self.minimum_construction_time:
            logger.error(f"Tempo de construção insuficiente: {time_elapsed/3600:.1f} horas")
            return False
        
        proof_hash = self._create_proof_hash(process.geolocation, description, "end")
        
        proof = ProofRecord(
            proof_hash=proof_hash,
            timestamp=time.time(),
            geolocation=process.geolocation,
            description=description
        )
        
        self.proof_registry[proof_hash] = proof
        process.end_proof = proof
        process.status = ProcessStatus.VALIDATING
        process.last_updated = time.time()
        
        logger.info(f"Prova de conclusão registrada: {process_id}")
        return True
    
    def add_resources_used(self, process_id: str, resources: Dict[str, float]) -> bool:
        """Adiciona recursos utilizados no processo"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        process.resources_used.update(resources)
        process.last_updated = time.time()
        
        return True
    
    def validate_by_consensus(self, process_id: str, validator_id: str) -> bool:
        """Valida processo por consenso comunitário"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        
        # Verifica se já foi validado
        if validator_id in process.validator_votes:
            return False
        
        # Verifica proximidade geográfica
        if not self._is_validator_nearby(validator_id, process.geolocation):
            logger.warning(f"Validador fora da área de validação: {validator_id}")
            return False
        
        process.validator_votes.append(validator_id)
        process.last_updated = time.time()
        
        # Verifica se tem consenso suficiente
        if len(process.validator_votes) >= 3:
            return self._auto_approve_process(process_id)
        
        return True
    
    def contest_process(self, process_id: str, contestor_id: str, reason: str) -> bool:
        """Contesta um processo em validação"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        
        if process.status != ProcessStatus.VALIDATING:
            return False
        
        process.status = ProcessStatus.CONTESTED
        process.last_updated = time.time()
        
        # Registra contestação no histórico
        contestation = f"CONTESTED: {contestor_id} - {reason} - {time.time()}"
        if process.m2_id in self.assets:
            self.assets[process.m2_id].validation_history.append(contestation)
        
        logger.info(f"Processo contestado: {process_id} por {contestor_id}")
        return True
    
    def _auto_approve_process(self, process_id: str) -> bool:
        """Aprova processo automaticamente por consenso"""
        process = self.processes[process_id]
        
        # Verifica coerência temporal
        time_elapsed = process.end_proof.timestamp - process.start_proof.timestamp
        if not self._validate_time_coherence(time_elapsed, process.resources_used):
            process.status = ProcessStatus.REJECTED
            return False
        
        # Calcula novo nível de desenvolvimento
        new_level = self._calculate_development_level(process.resources_used)
        
        # Atualiza asset
        if process.m2_id in self.assets:
            asset = self.assets[process.m2_id]
            asset.development_level = new_level
            asset.last_valuation = time.time()
            asset.current_value = self.development_values[new_level]
            asset.validation_history.append(f"APPROVED: {process_id} - {new_level.value}")
        
        process.status = ProcessStatus.APPROVED
        process.last_updated = time.time()
        
        logger.info(f"Processo aprovado automaticamente: {process_id}")
        return True
    
    def _validate_time_coherence(self, time_elapsed: float, resources: Dict[str, float]) -> bool:
        """Valida coerência entre tempo gasto e recursos utilizados"""
        # Regras de coerência básica
        hours_elapsed = time_elapsed / 3600
        
        # Mínimo de recursos por hora
        if hours_elapsed > 0:
            resource_per_hour = sum(resources.values()) / hours_elapsed
            if resource_per_hour < 0.1:  # Muito pouco recurso para muito tempo
                return False
        
        # Máximo de recursos por hora
        if hours_elapsed > 0:
            resource_per_hour = sum(resources.values()) / hours_elapsed
            if resource_per_hour > 10.0:  # Muitos recursos para pouco tempo
                return False
        
        return True
    
    def _calculate_development_level(self, resources: Dict[str, float]) -> DevelopmentLevel:
        """Calcula nível de desenvolvimento baseado em recursos utilizados"""
        total_resources = sum(resources.values())
        
        if total_resources < 1.0:
            return DevelopmentLevel.RAW
        elif total_resources < 5.0:
            return DevelopmentLevel.BASIC
        elif total_resources < 15.0:
            return DevelopmentLevel.DEVELOPED
        else:
            return DevelopmentLevel.ADVANCED
    
    def _is_validator_nearby(self, validator_id: str, geolocation: GeoLocation) -> bool:
        """Verifica se o validador está próximo ao local"""
        # Simulação de verificação de proximidade
        # Na prática, usaria geolocalização real do validador
        return True  # Simplificação para demonstração
    
    def _create_proof_hash(self, geolocation: GeoLocation, description: str, proof_type: str) -> str:
        """Cria hash único para prova"""
        data = f"{geolocation.to_hash()}_{description}_{proof_type}_{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get_asset_value(self, m2_id: str) -> Optional[float]:
        """Obtém valor atual de um m²"""
        if m2_id in self.assets:
            return self.assets[m2_id].current_value
        return None
    
    def get_process_status(self, process_id: str) -> Optional[ProcessStatus]:
        """Obtém status de um processo"""
        if process_id in self.processes:
            return self.processes[process_id].status
        return None
    
    def get_territorial_statistics(self) -> Dict:
        """Obtém estatísticas do território"""
        total_m2 = len(self.assets)
        development_counts = {level.value: 0 for level in DevelopmentLevel}
        
        for asset in self.assets.values():
            development_counts[asset.development_level.value] += 1
        
        total_value = sum(asset.current_value for asset in self.assets.values())
        
        return {
            "total_m2": total_m2,
            "development_distribution": development_counts,
            "total_territorial_value": total_value,
            "active_processes": len([p for p in self.processes.values() if p.status == ProcessStatus.VALIDATING]),
            "average_value_per_m2": total_value / total_m2 if total_m2 > 0 else 0
        }
    
    def simulate_contestation_resolution(self, process_id: str) -> bool:
        """Simula resolução de contestação pelo Conselho dos 5"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        
        if process.status != ProcessStatus.CONTESTED:
            return False
        
        # Simulação de julgamento do conselho
        # Na prática, usaria IA de auditoria e voto do conselho
        import random
        decision = random.choice([True, False])  # Decisão aleatória para simulação
        
        if decision:
            return self._auto_approve_process(process_id)
        else:
            process.status = ProcessStatus.REJECTED
            process.last_updated = time.time()
            return True

def main():
    """Exemplo de uso do Sistema Territorial"""
    
    sistema = SistemaTerritorial()
    
    print("=== SISTEMA TERRITORIAL MORAL MONEY ===")
    print()
    
    # Simula desenvolvimento de território
    geolocation = GeoLocation(latitude=40.7128, longitude=-74.0060)
    
    # 1. Registro de início
    print("1. Registrando início de desenvolvimento...")
    process_id = sistema.register_start_proof(
        geolocation=geolocation,
        description="Terreno bruto - início de desenvolvimento agrícola"
    )
    print(f"   Processo criado: {process_id}")
    print()
    
    # 2. Adiciona recursos utilizados
    print("2. Registrando recursos utilizados...")
    resources = {
        "sementes": 2.5,
        "fertilizante": 1.0,
        "irrigacao": 3.0,
        "mao_de_obra": 50.0
    }
    sistema.add_resources_used(process_id, resources)
    print(f"   Recursos registrados: {resources}")
    print()
    
    # 3. Simula tempo de desenvolvimento
    print("3. Simulando tempo de desenvolvimento...")
    # Simula 30 dias de desenvolvimento
    process = sistema.processes[process_id]
    process.end_proof = ProofRecord(
        proof_hash="simulated_end_proof",
        timestamp=time.time() + (30 * 24 * 3600),  # 30 dias depois
        geolocation=geolocation,
        description="Horta desenvolvida com sucesso"
    )
    process.status = ProcessStatus.VALIDATING
    print("   30 dias de desenvolvimento simulados")
    print()
    
    # 4. Validação por consenso
    print("4. Validando por consenso comunitário...")
    for i in range(3):
        validator_id = f"vizinho_{i+1}"
        sistema.validate_by_consensus(process_id, validator_id)
        print(f"   Validador {validator_id} aprovou")
    
    print()
    
    # 5. Verifica resultado
    print("5. Verificando resultado...")
    status = sistema.get_process_status(process_id)
    asset_value = sistema.get_asset_value(process.m2_id)
    
    print(f"   Status do processo: {status.value}")
    print(f"   Valor do m²: {asset_value} Buildcoins")
    print()
    
    # 6. Estatísticas territoriais
    print("6. Estatísticas territoriais...")
    stats = sistema.get_territorial_statistics()
    print(f"   Total de m²: {stats['total_m2']}")
    print(f"   Valor territorial total: {stats['total_territorial_value']:.2f} Buildcoins")
    print(f"   Distribuição de desenvolvimento: {stats['development_distribution']}")
    print()
    
    # 7. Simulação de contestação
    print("7. Simulando contestação...")
    if sistema.contest_process(process_id, "contestador_externo", "Desenvolvimento não corresponde aos recursos"):
        print("   Processo contestado com sucesso")
        
        # Resolução da contestação
        if sistema.simulate_contestation_resolution(process_id):
            print("   Contestado resolvida pelo conselho")
            final_status = sistema.get_process_status(process_id)
            print(f"   Status final: {final_status.value}")
    
    print()
    print("=== SISTEMA TERRITORIAL OPERACIONAL ===")
    print("Pronto para valoração de território sem vigilância!")

if __name__ == "__main__":
    main()