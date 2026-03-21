#!/usr/bin/env python3
"""
Sistema Financeiro Moral Money v1.2
===================================

Implementa a Grelha Salarial Oficial v1.2 para pagamentos no ecossistema.
Esta tabela é a única fonte de verdade para todos os pagamentos de trabalho.

Regras:
- TSU (Taxa Social Única): +23,75% sobre o custo hora para cálculo do ecossistema
- Retenção SS (Segurança Social): -11% para cálculo do valor líquido do trabalhador
- Multiplicador de reputação aplicado sobre o valor do escalão
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

class Escalao(Enum):
    """Escalões salariais da Grelha Salarial Oficial v1.2"""
    ESCALAO_1 = 1   # 5,50 € - Assistente Operacional (Base)
    ESCALAO_2 = 2   # 6,50 € - Assistente Operacional (Intermédio)
    ESCALAO_3 = 3   # 7,50 € - Assistente Operacional (Especializado)
    ESCALAO_4 = 4   # 8,50 € - Assistente Técnico (Início)
    ESCALAO_5 = 5   # 10,00 € - Assistente Técnico (Especializado)
    ESCALAO_6 = 6   # 12,00 € - Técnico Superior (Júnior)
    ESCALAO_7 = 7   # 14,00 € - Técnico Superior (Intermédio)
    ESCALAO_8 = 8   # 17,50 € - Técnico Superior (Sénior)
    ESCALAO_9 = 9   # 21,00 € - Especialista / Médico
    ESCALAO_10 = 10 # 25,00 € - Teto Ético de Responsabilidade

@dataclass
class CategoriaProfissional:
    """Categoria profissional associada a cada escalão"""
    nome: str
    descricao: str

@dataclass
class ConfiguracaoUsuario:
    """Configuração de usuário no sistema"""
    nome: str
    escalao: Escalao
    multiplicador_reputacao: float = 1.0

class SistemaFinanceiro:
    """
    Sistema de Pagamento baseado na Grelha Salarial Oficial v1.2
    
    Características:
    - Única fonte de verdade para pagamentos
    - Regras fiscais automáticas (TSU +23,75%)
    - Retenção de Segurança Social (-11%)
    - Multiplicadores de reputação
    """
    
    def __init__(self):
        # Grelha Salarial Oficial v1.2
        self.grelha_salarial = {
            Escalao.ESCALAO_1: 5.50,
            Escalao.ESCALAO_2: 6.50,
            Escalao.ESCALAO_3: 7.50,  # Nuno - Escalão 3
            Escalao.ESCALAO_4: 8.50,
            Escalao.ESCALAO_5: 10.00,
            Escalao.ESCALAO_6: 12.00,
            Escalao.ESCALAO_7: 14.00,
            Escalao.ESCALAO_8: 17.50,
            Escalao.ESCALAO_9: 21.00,
            Escalao.ESCALAO_10: 25.00
        }
        
        # Categorias profissionais
        self.categorias = {
            Escalao.ESCALAO_1: CategoriaProfissional("Assistente Operacional (Base)", "Operações básicas"),
            Escalao.ESCALAO_2: CategoriaProfissional("Assistente Operacional (Intermédio)", "Operações intermediárias"),
            Escalao.ESCALAO_3: CategoriaProfissional("Assistente Operacional (Especializado)", "Operações especializadas"),
            Escalao.ESCALAO_4: CategoriaProfissional("Assistente Técnico (Início)", "Funções técnicas iniciais"),
            Escalao.ESCALAO_5: CategoriaProfissional("Assistente Técnico (Especializado)", "Funções técnicas especializadas"),
            Escalao.ESCALAO_6: CategoriaProfissional("Técnico Superior (Júnior)", "Funções superiores júnior"),
            Escalao.ESCALAO_7: CategoriaProfissional("Técnico Superior (Intermédio)", "Funções superiores intermediárias"),
            Escalao.ESCALAO_8: CategoriaProfissional("Técnico Superior (Sénior)", "Funções superiores sénior"),
            Escalao.ESCALAO_9: CategoriaProfissional("Especialista / Médico", "Especialistas e profissionais médicos"),
            Escalao.ESCALAO_10: CategoriaProfissional("Teto Ético de Responsabilidade", "Máximo ético de responsabilidade")
        }
        
        # Regras fiscais - Módulo Fiscal v1.3
        self.tsu_rate = 0.2375  # 23,75% - Taxa Social Única
        self.seguro_at_rate = 0.015  # 1,5% - Seguro de Acidentes de Trabalho
        self.ss_rate = 0.11     # 11% - Segurança Social (trabalhador)
        
        # Configurações de usuários
        self.usuarios: Dict[str, ConfiguracaoUsuario] = {}
        
        # Configuração padrão do Nuno
        self.configurar_usuario_nuno()
        
        print("Sistema Financeiro v1.2 inicializado")
        print(f"Grelha Salarial: {len(self.grelha_salarial)} escalões configurados")
    
    def configurar_usuario_nuno(self):
        """Configura o utilizador 'Nuno' no Escalão 3 com multiplicador 1.8x"""
        nuno = ConfiguracaoUsuario(
            nome="Nuno",
            escalao=Escalao.ESCALAO_3,
            multiplicador_reputacao=1.8
        )
        self.usuarios["Nuno"] = nuno
        print(f"Usuário 'Nuno' configurado no Escalão 3 ({self.grelha_salarial[Escalao.ESCALAO_3]}€/h) com multiplicador 1.8x")
    
    def get_valor_hora_bruto(self, escalao: Escalao) -> float:
        """Obtém o valor hora bruto para um escalão"""
        return self.grelha_salarial.get(escalao, 0.0)
    
    def get_categoria(self, escalao: Escalao) -> CategoriaProfissional:
        """Obtém a categoria profissional para um escalão"""
        return self.categorias.get(escalao)
    
    def calcular_pagamento(self, horas: float, usuario: str) -> Dict:
        """
        Calcula pagamento completo com todas as regras fiscais (Módulo Fiscal v1.3)
        
        Retorna:
        {
            'horas': float,
            'escalao': int,
            'valor_hora_bruto': float,
            'valor_bruto_total': float,
            'multiplicador_reputacao': float,
            'valor_com_multiplicador': float,
            'tsu': float,
            'seguro_at': float,
            'custo_total_cooperativa': float,
            'retencao_ss': float,
            'retencao_irs': float,
            'valor_liquido_receber': float
        }
        """
        if usuario not in self.usuarios:
            raise ValueError(f"Usuário '{usuario}' não configurado no sistema")
        
        config = self.usuarios[usuario]
        valor_hora_bruto = self.get_valor_hora_bruto(config.escalao)
        
        # Cálculo base
        valor_bruto_total = horas * valor_hora_bruto
        
        # Aplica multiplicador de reputação
        valor_com_multiplicador = valor_bruto_total * config.multiplicador_reputacao
        
        # Calcula encargos da cooperativa (custo total empresa)
        tsu = valor_com_multiplicador * self.tsu_rate
        seguro_at = valor_com_multiplicador * self.seguro_at_rate
        custo_total_cooperativa = valor_com_multiplicador + tsu + seguro_at
        
        # Calcula retenções do trabalhador
        retencacao_ss = valor_com_multiplicador * self.ss_rate
        
        # Calcula IRS simplificado (progressivo mensal)
        salario_mensal_estimado = valor_com_multiplicador * 160  # 160h mensais estimados
        irs_rate = self.calcular_irs_rate(salario_mensal_estimado)
        retencacao_irs = valor_com_multiplicador * irs_rate
        
        valor_liquido_receber = valor_com_multiplicador - retencacao_ss - retencacao_irs
        
        return {
            'horas': horas,
            'escalao': config.escalao.value,
            'valor_hora_bruto': valor_hora_bruto,
            'valor_bruto_total': valor_bruto_total,
            'multiplicador_reputacao': config.multiplicador_reputacao,
            'valor_com_multiplicador': valor_com_multiplicador,
            'tsu': tsu,
            'seguro_at': seguro_at,
            'custo_total_cooperativa': custo_total_cooperativa,
            'retencao_ss': retencacao_ss,
            'retencao_irs': retencacao_irs,
            'valor_liquido_receber': valor_liquido_receber
        }
    
    def calcular_irs_rate(self, salario_mensal: float) -> float:
        """Calcula taxa de IRS simplificada (progressiva mensal)"""
        if salario_mensal <= 821:
            return 0.0  # Isento
        elif salario_mensal <= 1500:
            return 0.10  # 10%
        else:
            return 0.20  # 20%
    
    def gerar_recibo(self, horas: float, usuario: str) -> str:
        """
        Gera recibo no formato especificado:
        'Trabalho: 10h | Escalão 3 (7,50€) | Bónus Reputação (x1.8) | Custo Total Ecossistema (com TSU) | Valor Líquido a Receber'
        """
        calculo = self.calcular_pagamento(horas, usuario)
        
        recibo = (
            f"Trabalho: {calculo['horas']}h | "
            f"Escalão {calculo['escalao']} ({calculo['valor_hora_bruto']:.2f}€) | "
            f"Bónus Reputação (x{calculo['multiplicador_reputacao']:.1f}) | "
            f"Custo Total Cooperativa: {calculo['custo_total_cooperativa']:.2f}€ (com TSU) | "
            f"Valor Líquido a Receber: {calculo['valor_liquido_receber']:.2f}€"
        )
        
        return recibo
    
    def adicionar_usuario(self, nome: str, escalao: Escalao, multiplicador: float = 1.0):
        """Adiciona novo usuário ao sistema"""
        usuario = ConfiguracaoUsuario(
            nome=nome,
            escalao=escalao,
            multiplicador_reputacao=multiplicador
        )
        self.usuarios[nome] = usuario
        print(f"Usuário '{nome}' adicionado no Escalão {escalao.value} com multiplicador {multiplicador}x")
    
    def listar_grelha_salarial(self) -> List[Tuple[int, float, str]]:
        """Lista todos os escalões da grelha salarial"""
        lista = []
        for escalao in sorted(self.grelha_salarial.keys(), key=lambda x: x.value):
            valor = self.grelha_salarial[escalao]
            categoria = self.categorias[escalao].nome
            lista.append((escalao.value, valor, categoria))
        return lista
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas do sistema"""
        return {
            'total_usuarios': len(self.usuarios),
            'escaloes_disponiveis': len(self.grelha_salarial),
            'valor_minimo_hora': min(self.grelha_salarial.values()),
            'valor_maximo_hora': max(self.grelha_salarial.values()),
            'usuarios_configurados': list(self.usuarios.keys())
        }
    
    def simular_teste_stress(self, horas_mensais: int = 80, usuario: str = "Nuno") -> Dict:
        """
        Teste de Stress: Simula 80 horas mensais de trabalho e verifica sustentabilidade
        Cenário: Escalão 3 x 1.8 de reputação em terreno de 4 hectares (40.000€)
        """
        print(f"\n🧪 TESTE DE STRESS - {horas_mensais} HORAS MENSAL")
        print("=" * 60)
        
        # Cálculo do custo mensal
        calculo_hora = self.calcular_pagamento(1.0, usuario)
        custo_hora_cooperativa = calculo_hora['custo_total_cooperativa']
        
        custo_mensal = custo_hora_cooperativa * horas_mensais
        
        # Valorização do terreno (4 hectares = 40.000m²)
        valor_terreno_base = 40000.0  # 40.000€
        
        # Simulação de valorização por zona de impacto
        # Apenas a área trabalhada pode ser valorizada
        area_total = 40000  # m²
        area_trabalhada = horas_mensais * 100  # 100m² por hora trabalhada (estimativa)
        percentual_impactado = (area_trabalhada / area_total) * 100
        
        # Valorização proporcional ao trabalho
        valorizacao_terreno = valor_terreno_base * (percentual_impactado / 100) * 0.1  # 10% de valorização
        
        sustentavel = valorizacao_terreno >= custo_mensal
        
        resultado = {
            'horas_mensais': horas_mensais,
            'custo_hora_cooperativa': custo_hora_cooperativa,
            'custo_mensal': custo_mensal,
            'valor_terreno_base': valor_terreno_base,
            'area_total': area_total,
            'area_trabalhada': area_trabalhada,
            'percentual_impactado': percentual_impactado,
            'valorizacao_terreno': valorizacao_terreno,
            'sustentavel': sustentavel,
            'sobrevivencia_meses': valor_terreno_base / custo_mensal if custo_mensal > 0 else float('inf')
        }
        
        print(f"Usuário: {usuario}")
        print(f"Horas mensais: {horas_mensais}h")
        print(f"Custo hora cooperativa: {custo_hora_cooperativa:.2f}€")
        print(f"Custo mensal total: {custo_mensal:.2f}€")
        print(f"Valor terreno base: {valor_terreno_base:.2f}€")
        print(f"Área trabalhada: {area_trabalhada}m² ({percentual_impactado:.2f}%)")
        print(f"Valorização terreno: {valorizacao_terreno:.2f}€")
        print(f"Sustentável: {'✅ SIM' if sustentavel else '❌ NÃO'}")
        print(f"Sobrevivência: {resultado['sobrevivencia_meses']:.1f} meses")
        
        return resultado
    
    def gerar_recibo_cooperativa(self, horas: float, usuario: str) -> str:
        """
        Gera um Recibo de Vencimento de Cooperativa completo
        """
        calculo = self.calcular_pagamento(horas, usuario)
        config = self.usuarios[usuario]
        
        # Cálculo do salário mensal estimado
        horas_mensais_estimadas = 160  # 40h semanais
        salario_mensal_bruto = calculo['valor_com_multiplicador'] * horas_mensais_estimadas
        irs_rate = self.calcular_irs_rate(salario_mensal_bruto)
        
        recibo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RECIBO DE VENCIMENTO - COOPERATIVA                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Cooperativa: Moral Money Ecosystem                                          ║
║  Colaborador: {usuario:<56} ║
║  Escalão: {config.escalao.value} - {self.get_categoria(config.escalao).nome:<48} ║
║  Período: Mês corrente                                                       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  REMUNERAÇÃO BRUTA                                                           ║
║  Horas trabalhadas: {horas:>5.0f}h                                               ║
║  Valor hora bruto: {calculo['valor_hora_bruto']:>7.2f}€/h                                        ║
║  Multiplicador reputação: x{config.multiplicador_reputacao:.1f}                                         ║
║  Valor hora com bónus: {calculo['valor_com_multiplicador']/horas:>7.2f}€/h                                   ║
║                                                                              ║
║  Total Bruto: {calculo['valor_com_multiplicador']:>10.2f}€                                           ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  RETENÇÕES DO TRABALHADOR                                                    ║
║  Segurança Social (11%): {calculo['retencao_ss']:>10.2f}€                               ║
║  IRS ({irs_rate*100:2.0f}%): {calculo['retencao_irs']:>17.2f}€                                   ║
║                                                                              ║
║  Total Retenções: {calculo['retencao_ss'] + calculo['retencao_irs']:>11.2f}€                                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  REMUNERAÇÃO LÍQUIDA                                                         ║
║  Valor a receber: {calculo['valor_liquido_receber']:>13.2f}€                                       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  CUSTO TOTAL PARA A COOPERATIVA                                              ║
║  Valor bruto: {calculo['valor_com_multiplicador']:>15.2f}€                                       ║
║  TSU (23,75%): {calculo['tsu']:>14.2f}€                                         ║
║  Seguro AT (1,5%): {calculo['seguro_at']:>12.2f}€                                     ║
║                                                                              ║
║  Custo Total: {calculo['custo_total_cooperativa']:>15.2f}€                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Data: {time.strftime('%d/%m/%Y')}
Assinatura: ___________________________

Observações: Este recibo demonstra o rigor fiscal e contabilístico
            da Cooperativa Moral Money, conforme Código Cooperativo
            e legislação fiscal portuguesa vigente.
"""
        return recibo

def main():
    """Exemplo de uso do Sistema Financeiro"""
    
    sistema = SistemaFinanceiro()
    
    print("\n" + "="*80)
    print("SISTEMA FINANCEIRO MORAL MONEY v1.2")
    print("="*80)
    
    # 1. Listar grelha salarial
    print("\n1. GRELHA SALARIAL OFICIAL v1.2")
    print("-" * 50)
    for escalao, valor, categoria in sistema.listar_grelha_salarial():
        print(f"Escalão {escalao:2d}: {valor:5.2f}€/h - {categoria}")
    
    # 2. Exemplo com Nuno (10 horas)
    print("\n2. EXEMPLO DE PAGAMENTO - NUNO")
    print("-" * 50)
    
    horas_trabalho = 10
    recibo = sistema.gerar_recibo(horas_trabalho, "Nuno")
    print(recibo)
    
    # 3. Detalhes do cálculo
    print("\n3. DETALHES DO CÁLCULO")
    print("-" * 50)
    calculo = sistema.calcular_pagamento(horas_trabalho, "Nuno")
    
    print(f"Horas trabalhadas: {calculo['horas']}h")
    print(f"Escalão: {calculo['escalao']} ({calculo['valor_hora_bruto']:.2f}€/h)")
    print(f"Valor bruto total: {calculo['valor_bruto_total']:.2f}€")
    print(f"Multiplicador reputação: x{calculo['multiplicador_reputacao']:.1f}")
    print(f"Valor com multiplicador: {calculo['valor_com_multiplicador']:.2f}€")
    print(f"TSU (23,75%): {calculo['tsu']:.2f}€")
    print(f"Seguro AT (1,5%): {calculo['seguro_at']:.2f}€")
    print(f"Custo total cooperativa: {calculo['custo_total_cooperativa']:.2f}€")
    print(f"Retenção SS (11%): {calculo['retencao_ss']:.2f}€")
    print(f"Valor líquido a receber: {calculo['valor_liquido_receber']:.2f}€")
    
    # 4. Estatísticas
    print("\n4. ESTATÍSTICAS DO SISTEMA")
    print("-" * 50)
    stats = sistema.obter_estatisticas()
    for chave, valor in stats.items():
        print(f"{chave}: {valor}")
    
    print("\n" + "="*80)
    print("SISTEMA FINANCEIRO OPERACIONAL")
    print("Pronto para processar pagamentos conforme Grelha Salarial Oficial v1.2")
    print("="*80)

if __name__ == "__main__":
    main()