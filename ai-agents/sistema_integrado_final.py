#!/usr/bin/env python3
"""
Sistema Integrado Final para Moral Money

Implementa a integração completa de todos os sistemas:
- Sistema Territorial (Lastro)
- Sistema de Reputação Ativa
- Sistema de Cofre de Reserva
- IA de Auditoria
- Conselho dos 5
- Equivalência Ética
- Governança Horizontal
- P2P Offline

Cria um ecossistema completo e funcional do Moral Money.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

# Importa todos os sistemas implementados
from sistema_territorial import SistemaTerritorial, DevelopmentLevel, GeoLocation
from sistema_reputacao_ativa import SistemaReputacaoAtiva, WorkDomain, ReputationLevel
from sistema_cofre_reserva import SistemaCofreReserva, ReserveType, ConversionType
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
    EMERGENCY = "Emergency"
    OFFLINE = "Offline"

@dataclass
class SystemStatus:
    state: SystemState
    territorial_value: float
    total_buildcoins: float
    active_users: int
    system_health: float
    last_sync: float

class SistemaIntegradoFinal:
    """
    Sistema Integrado Final do Moral Money
    
    Coordenador de todos os subsistemas:
    1. Sistema Territorial - Lastro físico
    2. Sistema de Reputação Ativa - Mérito baseado em trabalho
    3. Sistema de Cofre de Reserva - Liquidez controlada
    4. IA de Auditoria - Validação automática
    5. Conselho dos 5 - Governança soberana
    6. Equivalência Ética - Distribuição justa
    7. Governança Horizontal - Decisões descentralizadas
    8. P2P Offline - Comunicação resiliente
    """
    
    def __init__(self, node_id: str = "moral_money_central"):
        self.node_id = node_id
        self.state = SystemState.INITIALIZING
        
        # Subsistemas
        self.sistema_territorial = None
        self.sistema_reputacao = None
        self.sistema_cofre = None
        self.ia_auditoria = None
        self.conselho_5 = None
        self.equivalencia_etica = None
        self.governanca = None
        self.p2p_network = None
        
        # Estado do sistema
        self.status = SystemStatus(
            state=SystemState.INITIALIZING,
            territorial_value=1.0,
            total_buildcoins=0.0,
            active_users=0,
            system_health=0.0,
            last_sync=0.0
        )
        
        # Configurações de integração
        self.integration_config = {
            "audit_interval": 30,      # Segundos
            "sync_interval": 60,       # Segundos
            "emergency_threshold": 0.3 # 30% de disponibilidade mínima
        }
        
        logger.info(f"Sistema Integrado Final iniciado: {self.node_id}")
    
    async def initialize_system(self) -> bool:
        """Inicializa todos os subsistemas"""
        logger.info("=== INICIALIZANDO SISTEMA INTEGRADO FINAL ===")
        
        try:
            # 1. Inicializa subsistemas básicos
            logger.info("1. Inicializando subsistemas básicos...")
            self.sistema_territorial = SistemaTerritorial()
            self.sistema_reputacao = SistemaReputacaoAtiva()
            self.sistema_cofre = SistemaCofreReserva()
            
            # 2. Inicializa subsistemas de IA e governança
            logger.info("2. Inicializando subsistemas de IA e governança...")
            self.ia_auditoria = MoralMoneyIA("http://localhost:9933")
            self.conselho_5 = ConselhoDos5("http://localhost:9933")
            self.equivalencia_etica = EquivalenciaEtica("http://localhost:9933")
            self.governanca = GovernancaHorizontal("http://localhost:9933")
            
            # 3. Inicializa rede P2P
            logger.info("3. Inicializando rede P2P...")
            self.p2p_network = P2POffline(self.node_id, 8080, NodeType.FULL_NODE)
            self.p2p_network.start_network()
            await asyncio.sleep(2)
            
            # 4. Configurações iniciais
            logger.info("4. Configurando parâmetros iniciais...")
            self._setup_initial_parameters()
            
            # 5. Atualiza estado
            self.state = SystemState.OPERATIONAL
            self.status.state = SystemState.OPERATIONAL
            self.status.last_sync = time.time()
            
            logger.info("=== SISTEMA INTEGRADO FINAL INICIALIZADO ===")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            self.state = SystemState.EMERGENCY
            return False
    
    def _setup_initial_parameters(self):
        """Configura parâmetros iniciais do sistema"""
        # Configura reservas iniciais
        self.sistema_cofre.add_reserve(ReserveType.CBDC, 1000000.0, "banco_central")
        self.sistema_cofre.add_reserve(ReserveType.EURO, 500000.0, "banco_tradicional")
        
        # Configura valor territorial inicial
        self.sistema_cofre.update_terratorial_value(1.0)
        self.status.territorial_value = 1.0
        
        # Configura parâmetros de reputação
        self.sistema_reputacao.base_reputation_gain = 10.0
    
    async def start_main_loop(self):
        """Inicia o loop principal do sistema integrado"""
        logger.info("Iniciando loop principal do sistema...")
        
        while self.state == SystemState.OPERATIONAL:
            try:
                # Executa ciclos de integração
                await self._integration_cycle()
                
                # Dorme por um intervalo
                await asyncio.sleep(self.integration_config["sync_interval"])
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(5)
    
    async def _integration_cycle(self):
        """Executa um ciclo completo de integração"""
        # 1. Atualiza status do sistema
        await self._update_system_status()
        
        # 2. Sincroniza subsistemas
        await self._sync_subsystems()
        
        # 3. Executa auditorias automáticas
        await self._execute_audits()
        
        # 4. Processa transações
        await self._process_transactions()
        
        # 5. Verifica saúde do sistema
        await self._check_system_health()
    
    async def _update_system_status(self):
        """Atualiza status geral do sistema"""
        try:
            # Atualiza valor territorial
            if self.sistema_cofre:
                self.status.territorial_value = self.sistema_cofre.territorial_value
            
            # Atualiza total de Buildcoins
            if self.sistema_territorial:
                stats = self.sistema_territorial.get_territorial_statistics()
                self.status.total_buildcoins = stats["total_territorial_value"]
                self.status.active_users = len(self.sistema_reputacao.reputations) if self.sistema_reputacao else 0
            
            # Atualiza saúde do sistema
            self.status.system_health = self._calculate_system_health()
            self.status.last_sync = time.time()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
    
    async def _sync_subsystems(self):
        """Sincroniza dados entre subsistemas"""
        try:
            # Sincroniza valor territorial entre cofre e territorial
            if self.sistema_cofre and self.sistema_territorial:
                # Atualiza valor territorial baseado no desenvolvimento
                territorial_stats = self.sistema_territorial.get_territorial_statistics()
                if territorial_stats["total_m2"] > 0:
                    avg_value = territorial_stats["total_territorial_value"] / territorial_stats["total_m2"]
                    self.sistema_cofre.update_terratorial_value(avg_value)
            
            # Sincroniza reputação e Buildcoins
            if self.sistema_reputacao and self.sistema_cofre:
                # Distribui Buildcoins baseados em reputação
                await self._distribute_buildcoins_by_reputation()
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
    
    async def _execute_audits(self):
        """Executa auditorias automáticas"""
        try:
            if self.ia_auditoria and self.sistema_territorial:
                # Auditoria de processos territoriais
                processes = self.sistema_territorial.processes
                
                for process_id, process in processes.items():
                    if process.status == "Validating":
                        # Executa auditoria
                        audit_result = await self._audit_process(process)
                        
                        if audit_result["approved"]:
                            # Aprova processo
                            self.sistema_territorial._auto_approve_process(process_id)
                        else:
                            # Contesta processo
                            self.sistema_territorial.contest_process(
                                process_id, "IA_Auditoria", audit_result["reason"]
                            )
            
        except Exception as e:
            logger.error(f"Erro na auditoria: {e}")
    
    async def _audit_process(self, process) -> Dict:
        """Audita um processo territorial"""
        try:
            # Simula auditoria
            time_elapsed = process.end_proof.timestamp - process.start_proof.timestamp
            resources = process.resources_used
            
            # Verifica coerência
            if time_elapsed < 7 * 24 * 3600:  # Menos de 7 dias
                return {"approved": False, "reason": "Tempo insuficiente"}
            
            if sum(resources.values()) < 1.0:  # Poucos recursos
                return {"approved": False, "reason": "Recursos insuficientes"}
            
            return {"approved": True, "reason": "Processo válido"}
            
        except Exception:
            return {"approved": False, "reason": "Erro na auditoria"}
    
    async def _process_transactions(self):
        """Processa transações entre subsistemas"""
        try:
            # Processa conversões de moeda
            if self.sistema_cofre:
                conversions = self.sistema_cofre.conversions
                for conv_id, conversion in conversions.items():
                    if conversion.conversion_type == ConversionType.DEPOSIT:
                        # Processa depósito
                        await self._process_deposit(conversion)
                    elif conversion.conversion_type == ConversionType.WITHDRAWAL:
                        # Processa saque
                        await self._process_withdrawal(conversion)
            
        except Exception as e:
            logger.error(f"Erro no processamento de transações: {e}")
    
    async def _process_deposit(self, conversion):
        """Processa depósito de moeda externa"""
        try:
            # Atualiza reputação do contribuidor
            if self.sistema_reputacao:
                self.sistema_reputacao.register_contribution(
                    contributor_id=conversion.account_id,
                    work_domain=WorkDomain.GOVERNANCE,  # Contribuição financeira
                    work_description=f"Depósito de {conversion.source_amount} {conversion.source_type.value}",
                    hours_worked=0.0,  # Não é trabalho direto
                    skill_level=0.5,
                    resources_used={conversion.source_type.value: conversion.source_amount}
                )
            
            # Atualiza estatísticas
            logger.info(f"Depósito processado: {conversion.source_amount} → {conversion.target_amount}")
            
        except Exception as e:
            logger.error(f"Erro ao processar depósito: {e}")
    
    async def _process_withdrawal(self, conversion):
        """Processa saque de moeda externa"""
        try:
            # Verifica se o usuário tem reputação suficiente
            if self.sistema_reputacao:
                reputation = self.sistema_reputacao.get_current_reputation(conversion.account_id)
                
                # Penaliza saques muito cedo (menos de 90 dias)
                if conversion.fees > conversion.target_amount * 0.1:  # Taxa alta
                    self.sistema_reputacao.apply_slashing(
                        conversion.account_id, 1.0, "saque_antecipado"
                    )
            
            logger.info(f"Saque processado: {conversion.source_amount} → {conversion.target_amount}")
            
        except Exception as e:
            logger.error(f"Erro ao processar saque: {e}")
    
    async def _distribute_buildcoins_by_reputation(self):
        """Distribui Buildcoins baseados na reputação"""
        try:
            if not self.sistema_reputacao or not self.sistema_cofre:
                return
            
            # Calcula distribuição baseada em reputação
            total_reputation = sum(r.total_reputation for r in self.sistema_reputacao.reputations.values())
            
            if total_reputation == 0:
                return
            
            # Distribui Buildcoins proporcionais à reputação
            for account_id, reputation in self.sistema_reputacao.reputations.items():
                if reputation.total_reputation > 0:
                    # Calcula Buildcoins a receber
                    buildcoins = (reputation.total_reputation / total_reputation) * 100  # 100 Buildcoins de recompensa
                    
                    # Converte para Buildcoins usando o cofre
                    conversion = self.sistema_cofre.deposit_external_currency(
                        account_id, buildcoins * self.sistema_cofre.territorial_value, ReserveType.CBDC
                    )
                    
                    if conversion:
                        logger.info(f"Distribuição para {account_id}: {conversion.target_amount:.2f} Buildcoins")
            
        except Exception as e:
            logger.error(f"Erro na distribuição: {e}")
    
    async def _check_system_health(self):
        """Verifica saúde do sistema integrado"""
        try:
            health_score = 1.0
            
            # Verifica saúde do cofre
            if self.sistema_cofre:
                liquidity_status = self.sistema_cofre.get_liquidity_status()
                if liquidity_status == "Emergency":
                    health_score -= 0.5
                elif liquidity_status == "Restricted":
                    health_score -= 0.2
            
            # Verifica saúde territorial
            if self.sistema_territorial:
                stats = self.sistema_territorial.get_territorial_statistics()
                if stats["total_m2"] == 0:
                    health_score -= 0.3
            
            # Verifica saúde da reputação
            if self.sistema_reputacao:
                stats = self.sistema_reputacao.get_reputation_statistics()
                if stats["total_contributors"] == 0:
                    health_score -= 0.3
            
            self.status.system_health = max(health_score, 0.0)
            
            # Verifica condições de emergência
            if self.status.system_health < self.integration_config["emergency_threshold"]:
                logger.warning(f"SAÚDE DO SISTEMA CRÍTICA: {self.status.system_health:.2f}")
                await self._activate_emergency_protocols()
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde: {e}")
    
    async def _activate_emergency_protocols(self):
        """Ativa protocolos de emergência"""
        try:
            logger.critical("ATIVANDO PROTOCOLOS DE EMERGÊNCIA")
            
            # Simula estresse de mercado
            if self.sistema_cofre:
                self.sistema_cofre.simulate_market_stress(0.5)
            
            # Aumenta taxas de saque
            if self.sistema_reputacao:
                for account_id in self.sistema_reputacao.reputations:
                    # Penaliza saques em massa
                    self.sistema_reputacao.apply_slashing(account_id, 2.0, "emergencia_sistema")
            
            self.state = SystemState.EMERGENCY
            
        except Exception as e:
            logger.error(f"Erro nos protocolos de emergência: {e}")
    
    def _calculate_system_health(self) -> float:
        """Calcula saúde geral do sistema"""
        score = 1.0
        
        # Verifica subsistemas críticos
        critical_systems = [
            self.sistema_territorial,
            self.sistema_reputacao,
            self.sistema_cofre,
            self.ia_auditoria
        ]
        
        operational_systems = sum(1 for s in critical_systems if s is not None)
        total_systems = len(critical_systems)
        
        score = operational_systems / total_systems
        
        return score
    
    def get_comprehensive_status(self) -> Dict:
        """Obtém status completo do sistema integrado"""
        try:
            status = {
                "node_id": self.node_id,
                "state": self.state.value,
                "territorial_value": self.status.territorial_value,
                "total_buildcoins": self.status.total_buildcoins,
                "active_users": self.status.active_users,
                "system_health": self.status.system_health,
                "last_sync": self.status.last_sync,
                "subsystems": {
                    "territorial": self.sistema_territorial is not None,
                    "reputation": self.sistema_reputacao is not None,
                    "cofre": self.sistema_cofre is not None,
                    "ia_auditoria": self.ia_auditoria is not None,
                    "conselho_5": self.conselho_5 is not None,
                    "equivalencia_etica": self.equivalencia_etica is not None,
                    "governanca": self.governanca is not None,
                    "p2p_network": self.p2p_network is not None
                }
            }
            
            # Adiciona estatísticas detalhadas
            if self.sistema_territorial:
                status["territorial_stats"] = self.sistema_territorial.get_territorial_statistics()
            
            if self.sistema_reputacao:
                status["reputation_stats"] = self.sistema_reputacao.get_reputation_statistics()
            
            if self.sistema_cofre:
                status["cofre_stats"] = self.sistema_cofre.get_conversion_statistics()
            
            return status
            
        except Exception as e:
            logger.error(f"Erro ao obter status completo: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Encerra o sistema integrado"""
        logger.info("=== ENCERRANDO SISTEMA INTEGRADO FINAL ===")
        
        self.state = SystemState.OFFLINE
        
        # Encerra P2P
        if self.p2p_network:
            self.p2p_network.stop_network()
        
        logger.info("Sistema Integrado Final encerrado")

async def main():
    """Exemplo de uso do Sistema Integrado Final"""
    
    # Cria sistema integrado
    sistema = SistemaIntegradoFinal("moral_money_central")
    
    # Inicializa
    success = await sistema.initialize_system()
    if not success:
        logger.error("Falha na inicialização do sistema")
        return
    
    # Inicia loop principal
    await sistema.start_main_loop()
    
    try:
        print("=== SISTEMA INTEGRADO FINAL MORAL MONEY ===")
        print("Todos os subsistemas estão operacionais!")
        print()
        
        # Mostra status inicial
        status = sistema.get_comprehensive_status()
        print("=== STATUS DO SISTEMA ===")
        print(f"Estado: {status['state']}")
        print(f"Nó: {status['node_id']}")
        print(f"Valor Territorial: {status['territorial_value']} Buildcoins/m²")
        print(f"Total de Buildcoins: {status['total_buildcoins']:.2f}")
        print(f"Usuários Ativos: {status['active_users']}")
        print(f"Saúde do Sistema: {status['system_health']:.2f}")
        print()
        
        # Simula operações
        print("=== SIMULANDO OPERAÇÕES ===")
        
        # 1. Desenvolvimento territorial
        print("1. Desenvolvimento territorial...")
        geolocation = GeoLocation(latitude=40.7128, longitude=-74.0060)
        process_id = sistema.sistema_territorial.register_start_proof(
            geolocation, "Desenvolvimento agrícola"
        )
        print(f"   Processo territorial iniciado: {process_id}")
        
        # 2. Contribuição de trabalho
        print("2. Contribuição de trabalho...")
        contrib_id = sistema.sistema_reputacao.register_contribution(
            "trabalhador_001",
            WorkDomain.AGRICULTURE,
            "Plantio e cultivo",
            100.0,
            0.8,
            {"sementes": 10.0, "fertilizante": 5.0}
        )
        print(f"   Contribuição registrada: {contrib_id}")
        
        # 3. Depósito de moeda externa
        print("3. Depósito de moeda externa...")
        deposito = sistema.sistema_cofre.deposit_external_currency(
            "investidor_externo", 50000.0, ReserveType.CBDC
        )
        if deposito:
            print(f"   Depósito: {deposito.source_amount} CBDC → {deposito.target_amount:.2f} Buildcoins")
        
        print()
        print("=== SISTEMA INTEGRADO OPERACIONAL ===")
        print("Pronto para operação completa do Moral Money!")
        
        # Mantém o sistema rodando
        while True:
            await asyncio.sleep(30)
            status = sistema.get_comprehensive_status()
            print(f"Batimento cardíaco - Usuários: {status['active_users']}, Saúde: {status['system_health']:.2f}")
            
    except KeyboardInterrupt:
        print("\nEncerrando sistema...")
        await sistema.shutdown()

if __name__ == "__main__":
    asyncio.run(main())