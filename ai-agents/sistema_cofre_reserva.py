#!/usr/bin/env python3
"""
Sistema de Cofre de Reserva para Moral Money

Implementa o mecanismo de lastro territorial para Buildcoins com liquidez controlada.
Sistema de conversão entre moeda externa (CBDCs/Euros) e Buildcoins baseado em valorização territorial.

Princípios:
- Lastro territorial: 1 Buildcoin = 1m² de território desenvolvido
- Liquidez controlada para entrada/saída da comunidade
- Proteção contra especulação externa
- Conversão automática baseada em valorização real
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

class ReserveType(Enum):
    CBDC = "CBDC"           # Central Bank Digital Currency
    EURO = "Euro"          # Euro tradicional
    GOLD = "Gold"          # Ouro (reserva de emergência)
    ENERGY = "Energy"      # Energia (reserva alternativa)

class ConversionType(Enum):
    DEPOSIT = "Deposit"     # Entrada de capital externo
    WITHDRAWAL = "Withdrawal"  # Saída de capital
    EXCHANGE = "Exchange"   # Troca entre reservas

class LiquidityStatus(Enum):
    NORMAL = "Normal"
    RESTRICTED = "Restricted"
    EMERGENCY = "Emergency"

@dataclass
class ReserveEntry:
    entry_id: str
    reserve_type: ReserveType
    amount: float
    timestamp: float
    source_account: str
    target_account: Optional[str] = None

@dataclass
class ConversionRecord:
    conversion_id: str
    conversion_type: ConversionType
    source_amount: float
    source_type: ReserveType
    target_amount: float
    target_type: str  # "Buildcoin" ou ReserveType
    exchange_rate: float
    fees: float
    timestamp: float
    account_id: str

@dataclass
class LiquidityPool:
    reserve_type: ReserveType
    total_amount: float
    available_amount: float
    locked_amount: float
    last_updated: float

class SistemaCofreReserva:
    """
    Sistema de Cofre de Reserva
    
    Características:
    - Lastro territorial para Buildcoins
    - Liquidez controlada com taxas progressivas
    - Proteção contra saques massivos
    - Conversão automática baseada em valorização territorial
    """
    
    def __init__(self):
        # Armazenamento de reservas
        self.reserves: Dict[ReserveType, LiquidityPool] = {}
        self.conversions: Dict[str, ConversionRecord] = {}
        self.territorial_value: float = 1.0  # Valor base do m² em Buildcoins
        
        # Configurações de liquidez
        self.daily_withdrawal_limit = 100000.0  # Limite diário de saque
        self.withdrawal_fees = {
            "0-30": 0.0,      # 0% nos primeiros 30 dias
            "31-90": 0.05,    # 5% de 31 a 90 dias
            "91-180": 0.10,   # 10% de 91 a 180 dias
            "181+": 0.20     # 20% após 180 dias
        }
        
        # Configurações de reserva
        self.reserve_ratios = {
            ReserveType.CBDC: 0.7,    # 70% em CBDCs
            ReserveType.EURO: 0.2,    # 20% em Euros
            ReserveType.GOLD: 0.05,   # 5% em ouro
            ReserveType.ENERGY: 0.05  # 5% em energia
        }
        
        # Inicializa reservas
        for reserve_type in ReserveType:
            self.reserves[reserve_type] = LiquidityPool(
                reserve_type=reserve_type,
                total_amount=0.0,
                available_amount=0.0,
                locked_amount=0.0,
                last_updated=time.time()
            )
        
        logger.info("Sistema de Cofre de Reserva inicializado")
    
    def update_terratorial_value(self, new_value: float):
        """Atualiza o valor territorial base (Buildcoins por m²)"""
        old_value = self.territorial_value
        self.territorial_value = max(new_value, 0.1)  # Mínimo de 0.1
        
        logger.info(f"Valor territorial atualizado: {old_value:.2f} → {self.territorial_value:.2f} Buildcoins/m²")
    
    def add_reserve(self, reserve_type: ReserveType, amount: float, source_account: str) -> bool:
        """Adiciona reserva ao cofre"""
        if amount <= 0:
            return False
        
        pool = self.reserves[reserve_type]
        pool.total_amount += amount
        pool.available_amount += amount
        pool.last_updated = time.time()
        
        # Registra entrada
        entry = ReserveEntry(
            entry_id=f"RESERVE_{int(time.time())}_{source_account[:8]}",
            reserve_type=reserve_type,
            amount=amount,
            timestamp=time.time(),
            source_account=source_account
        )
        
        logger.info(f"Reserva adicionada: {amount} {reserve_type.value} por {source_account}")
        return True
    
    def calculate_withdrawal_fee(self, days_held: int) -> float:
        """Calcula taxa de saque baseada no tempo de permanência"""
        if days_held <= 30:
            return self.withdrawal_fees["0-30"]
        elif days_held <= 90:
            return self.withdrawal_fees["31-90"]
        elif days_held <= 180:
            return self.withdrawal_fees["91-180"]
        else:
            return self.withdrawal_fees["181+"]
    
    def deposit_external_currency(self, account_id: str, amount: float, 
                                 reserve_type: ReserveType) -> Optional[ConversionRecord]:
        """Depósito de moeda externa para obtenção de Buildcoins"""
        if amount <= 0:
            return None
        
        # Verifica disponibilidade da reserva
        pool = self.reserves[reserve_type]
        if pool.available_amount < amount:
            logger.error(f"Reserva insuficiente: {pool.available_amount} < {amount}")
            return None
        
        # Calcula taxa de conversão (spread)
        spread = 0.02  # 2% de spread
        
        # Converte para Buildcoins baseado no valor territorial
        buildcoins_received = (amount * (1 - spread)) / self.territorial_value
        
        # Atualiza reservas
        pool.available_amount -= amount
        pool.locked_amount += amount
        
        # Registra conversão
        conversion = ConversionRecord(
            conversion_id=f"CONV_{int(time.time())}_{account_id[:8]}",
            conversion_type=ConversionType.DEPOSIT,
            source_amount=amount,
            source_type=reserve_type,
            target_amount=buildcoins_received,
            target_type="Buildcoin",
            exchange_rate=1.0 / self.territorial_value,
            fees=amount * spread,
            timestamp=time.time(),
            account_id=account_id
        )
        
        self.conversions[conversion.conversion_id] = conversion
        
        logger.info(f"Depósito realizado: {amount} {reserve_type.value} → {buildcoins_received:.2f} Buildcoins")
        return conversion
    
    def withdraw_external_currency(self, account_id: str, buildcoins_amount: float,
                                  reserve_type: ReserveType, days_held: int) -> Optional[ConversionRecord]:
        """Saque de moeda externa trocando Buildcoins"""
        if buildcoins_amount <= 0:
            return None
        
        # Calcula taxa de saque baseada no tempo
        fee_rate = self.calculate_withdrawal_fee(days_held)
        
        # Calcula valor em moeda externa
        base_value = buildcoins_amount * self.territorial_value
        fees = base_value * fee_rate
        net_value = base_value - fees
        
        # Verifica disponibilidade da reserva
        pool = self.reserves[reserve_type]
        if pool.locked_amount < net_value:
            logger.error(f"Reserva bloqueada insuficiente: {pool.locked_amount} < {net_value}")
            return None
        
        # Atualiza reservas
        pool.locked_amount -= net_value
        pool.available_amount += net_value
        
        # Registra conversão
        conversion = ConversionRecord(
            conversion_id=f"CONV_{int(time.time())}_{account_id[:8]}",
            conversion_type=ConversionType.WITHDRAWAL,
            source_amount=buildcoins_amount,
            source_type="Buildcoin",
            target_amount=net_value,
            target_type=reserve_type.value,
            exchange_rate=self.territorial_value,
            fees=fees,
            timestamp=time.time(),
            account_id=account_id
        )
        
        self.conversions[conversion.conversion_id] = conversion
        
        logger.info(f"Saque realizado: {buildcoins_amount:.2f} Buildcoins → {net_value:.2f} {reserve_type.value} (taxa: {fee_rate*100:.1f}%)")
        return conversion
    
    def emergency_liquidity_withdrawal(self, amount: float, reserve_type: ReserveType) -> bool:
        """Saque de liquidez de emergência (para situações críticas)"""
        pool = self.reserves[reserve_type]
        
        # Em emergência, pode usar até 50% das reservas totais
        max_emergency = pool.total_amount * 0.5
        
        if amount > max_emergency:
            logger.error(f"Saque de emergência excede limite: {amount} > {max_emergency}")
            return False
        
        pool.available_amount -= amount
        pool.total_amount -= amount
        
        logger.warning(f"Saque de emergência: {amount} {reserve_type.value}")
        return True
    
    def get_liquidity_status(self) -> LiquidityStatus:
        """Obtém status da liquidez do cofre"""
        total_reserves = sum(pool.total_amount for pool in self.reserves.values())
        total_available = sum(pool.available_amount for pool in self.reserves.values())
        
        if total_available <= 0:
            return LiquidityStatus.EMERGENCY
        elif total_available / total_reserves < 0.1:  # Menos de 10% disponível
            return LiquidityStatus.RESTRICTED
        else:
            return LiquidityStatus.NORMAL
    
    def get_reserve_distribution(self) -> Dict[str, float]:
        """Obtém distribuição das reservas"""
        total_reserves = sum(pool.total_amount for pool in self.reserves.values())
        
        distribution = {}
        for reserve_type, pool in self.reserves.items():
            percentage = (pool.total_amount / total_reserves * 100) if total_reserves > 0 else 0
            distribution[reserve_type.value] = {
                "total": pool.total_amount,
                "available": pool.available_amount,
                "locked": pool.locked_amount,
                "percentage": percentage
            }
        
        return distribution
    
    def get_conversion_statistics(self) -> Dict:
        """Obtém estatísticas de conversões"""
        total_deposits = sum(1 for c in self.conversions.values() if c.conversion_type == ConversionType.DEPOSIT)
        total_withdrawals = sum(1 for c in self.conversions.values() if c.conversion_type == ConversionType.WITHDRAWAL)
        
        total_fees = sum(c.fees for c in self.conversions.values())
        
        # Volume por tipo de reserva
        volume_by_type = {}
        for reserve_type in ReserveType:
            deposits = sum(c.source_amount for c in self.conversions.values() 
                          if c.conversion_type == ConversionType.DEPOSIT and c.source_type == reserve_type)
            withdrawals = sum(c.target_amount for c in self.conversions.values() 
                            if c.conversion_type == ConversionType.WITHDRAWAL and c.target_type == reserve_type.value)
            volume_by_type[reserve_type.value] = {
                "deposits": deposits,
                "withdrawals": withdrawals,
                "net_flow": deposits - withdrawals
            }
        
        return {
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_fees_collected": total_fees,
            "volume_by_type": volume_by_type,
            "liquidity_status": self.get_liquidity_status().value,
            "territorial_value": self.territorial_value
        }
    
    def simulate_market_stress(self, stress_factor: float) -> bool:
        """Simula estresse de mercado e ajusta políticas de liquidez"""
        if stress_factor <= 0 or stress_factor > 1:
            return False
        
        # Aumenta taxas de saque em situações de estresse
        for key in self.withdrawal_fees:
            self.withdrawal_fees[key] *= (1 + stress_factor)
        
        # Reduz limite diário de saque
        self.daily_withdrawal_limit *= (1 - stress_factor)
        
        logger.warning(f"Estresse de mercado detectado (fator: {stress_factor:.2f}). Políticas de liquidez ajustadas.")
        return True

def main():
    """Exemplo de uso do Sistema de Cofre de Reserva"""
    
    cofre = SistemaCofreReserva()
    
    print("=== SISTEMA DE COFRE DE RESERVA ===")
    print()
    
    # 1. Configuração inicial de reservas
    print("1. Configurando reservas iniciais...")
    cofre.add_reserve(ReserveType.CBDC, 500000.0, "banco_central")
    cofre.add_reserve(ReserveType.EURO, 200000.0, "banco_tradicional")
    cofre.add_reserve(ReserveType.GOLD, 50000.0, "reserva_ouro")
    cofre.add_reserve(ReserveType.ENERGY, 50000.0, "fornecedor_energia")
    
    print("   Reservas configuradas")
    print()
    
    # 2. Depósito de moeda externa
    print("2. Realizando depósito de moeda externa...")
    deposito = cofre.deposit_external_currency("investidor_externo", 10000.0, ReserveType.CBDC)
    if deposito:
        print(f"   Depósito: {deposito.source_amount} CBDC → {deposito.target_amount:.2f} Buildcoins")
    print()
    
    # 3. Atualização do valor territorial
    print("3. Atualizando valor territorial...")
    cofre.update_terratorial_value(1.5)  # Valorização do território
    print(f"   Novo valor: {cofre.territorial_value} Buildcoins/m²")
    print()
    
    # 4. Saque de moeda externa
    print("4. Realizando saque de moeda externa...")
    # Simula 60 dias de permanência
    saque = cofre.withdraw_external_currency("investidor_externo", 5000.0, ReserveType.CBDC, 60)
    if saque:
        print(f"   Saque: {saque.source_amount} Buildcoins → {saque.target_amount:.2f} CBDC")
        print(f"   Taxa aplicada: {saque.fees:.2f}")
    print()
    
    # 5. Estatísticas do cofre
    print("5. Verificando estatísticas do cofre...")
    stats = cofre.get_conversion_statistics()
    distribution = cofre.get_reserve_distribution()
    
    print(f"   Depósitos totais: {stats['total_deposits']}")
    print(f"   Saques totais: {stats['total_withdrawals']}")
    print(f"   Taxas coletadas: {stats['total_fees_collected']:.2f}")
    print(f"   Status de liquidez: {stats['liquidity_status']}")
    print()
    
    print("   Distribuição de reservas:")
    for reserve_type, data in distribution.items():
        print(f"     {reserve_type}: {data['total']:.0f} total, {data['available']:.0f} disponível")
    print()
    
    # 6. Simulação de estresse
    print("6. Simulando estresse de mercado...")
    cofre.simulate_market_stress(0.3)  # 30% de estresse
    print("   Políticas de liquidez ajustadas")
    print()
    
    print("=== SISTEMA DE COFRE DE RESERVA OPERACIONAL ===")
    print("Pronto para gerenciar liquidez e lastro territorial!")

if __name__ == "__main__":
    main()