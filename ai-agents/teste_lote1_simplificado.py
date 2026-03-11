#!/usr/bin/env python3
"""
TESTE DO LOTE 1 - SIMULAÇÃO SIMPLIFICADA
========================================

Comparação entre versão "alucinada" (anterior) vs "realista" (atual)
com novos parâmetros de zona de impacto.
"""

def simular_lote1_realista():
    """Simulação realista do Lote 1 - versão simplificada"""
    
    print("=" * 80)
    print("TESTE DO LOTE 1 - SIMULAÇÃO REALISTA (VERSÃO SIMPLIFICADA)")
    print("=" * 80)
    
    # 1. INVESTIDOR APORTA 40.000 m²
    print("\n1. INVESTIDOR APORTA 40.000 m²")
    print("-" * 50)
    
    area_total = 40000  # m²
    valor_base_m2 = 0.5  # Buildcoins/m²
    valor_investidor = area_total * valor_base_m2
    
    print(f"Área total: {area_total:,} m²")
    print(f"Valor base: {valor_base_m2} Buildcoins/m²")
    print(f"Valor do investidor: {valor_investidor:,} Buildcoins")
    
    # 2. NUNO (VETERANO) REGISTA 10 HORAS DE LIMPEZA
    print("\n2. NUNO (VETERANO) REGISTA 10 HORAS DE LIMPEZA")
    print("-" * 50)
    
    horas_trabalho = 10
    valor_hora_base = 6.0  # 6€ por hora (valor realista)
    area_trabalhada = 1000  # m² (apenas a área que Nuno realmente trabalhou)
    
    # Cálculo baseado no valor da hora de trabalho
    ganho_bruto_nuno = horas_trabalho * valor_hora_base
    
    print(f"Horas trabalhadas: {horas_trabalho} horas")
    print(f"Valor hora base: {valor_hora_base}€/hora")
    print(f"Área trabalhada: {area_trabalhada} m² (zona de impacto)")
    print(f"Ganho bruto por hora: {ganho_bruto_nuno/horas_trabalho:.2f}€/hora")
    
    # 3. APLICA LÓGICA DE ZONA DE IMPACTO
    print("\n3. LÓGICA DE ZONA DE IMPACTO")
    print("-" * 50)
    print("Apenas a área trabalhada pode valorizar")
    print(f"Área total: {area_total:,} m²")
    print(f"Área trabalhada: {area_trabalhada} m²")
    print(f"Percentual impactado: {(area_trabalhada/area_total)*100:.2f}%")
    
    # 4. CALCULA O VALOR DO ECOSISTEMA
    print("\n4. VALOR DO ECOSISTEMA")
    print("-" * 50)
    
    # Valor base do ecossistema (sem valorização)
    valor_base_ecossistema = area_total * valor_base_m2
    
    # Valorização baseada no trabalho realizado (não na área)
    # O trabalho do Nuno gera valor equivalente ao seu ganho bruto
    valorizacao_total = ganho_bruto_nuno
    valor_ecossistema_realista = valor_base_ecossistema + valorizacao_total
    
    print(f"Valor base do ecossistema: {valor_base_ecossistema:,} Buildcoins")
    print(f"Valorização total: {valorizacao_total:,} Buildcoins")
    print(f"Valor do ecossistema realista: {valor_ecossistema_realista:,} Buildcoins")
    
    # 5. GANHO DO NUNO COM MULTIPLICADOR DE REPUTAÇÃO
    print("\n5. GANHO DO NUNO (MULTIPLICADOR 1.8x)")
    print("-" * 50)
    
    multiplicador_reputacao = 1.8
    ganho_nuno = ganho_bruto_nuno * multiplicador_reputacao
    
    print(f"Ganho bruto do Nuno: {ganho_bruto_nuno:,} Buildcoins")
    print(f"Multiplicador de reputação: {multiplicador_reputacao}x")
    print(f"Ganho final do Nuno: {ganho_nuno:,} Buildcoins")
    
    # 6. COMPARAÇÃO COM VERSÃO "ALUCINADA"
    print("\n6. COMPARAÇÃO ALUCINADA vs REALISTA")
    print("-" * 50)
    
    # Versão "alucinada" (anterior) - valorizava toda a área
    valorizacao_alucinada = valor_base_ecossistema * 0.4  # 40% de valorização
    valor_ecossistema_alucinado = valor_base_ecossistema + valorizacao_alucinada
    ganho_nuno_alucinado = valorizacao_alucinada * multiplicador_reputacao
    
    print("VERSÃO ALUCINADA (ANTERIOR):")
    print(f"  Valor do ecossistema: {valor_ecossistema_alucinado:,} Buildcoins")
    print(f"  Ganho do Nuno: {ganho_nuno_alucinado:,} Buildcoins")
    print(f"  Percentual do ecossistema: {(ganho_nuno_alucinado/valor_ecossistema_alucinado)*100:.2f}%")
    
    print("\nVERSÃO REALISTA (ATUAL):")
    print(f"  Valor do ecossistema: {valor_ecossistema_realista:,} Buildcoins")
    print(f"  Ganho do Nuno: {ganho_nuno:,} Buildcoins")
    print(f"  Percentual do ecossistema: {(ganho_nuno/valor_ecossistema_realista)*100:.2f}%")
    
    # 7. DIFERENÇA ENTRE AS SIMULAÇÕES
    print("\n7. DIFERENÇA ENTRE SIMULAÇÕES")
    print("-" * 50)
    
    diferenca_valor_ecossistema = valor_ecossistema_alucinado - valor_ecossistema_realista
    diferenca_ganho_nuno = ganho_nuno_alucinado - ganho_nuno
    
    print(f"Diferença no valor do ecossistema: {diferenca_valor_ecossistema:,} Buildcoins")
    print(f"Diferença no ganho do Nuno: {diferenca_ganho_nuno:,} Buildcoins")
    print(f"Redução percentual do ecossistema: {(diferenca_valor_ecossistema/valor_ecossistema_alucinado)*100:.2f}%")
    print(f"Redução percentual do ganho: {(diferenca_ganho_nuno/ganho_nuno_alucinado)*100:.2f}%")
    
    print("\n" + "=" * 80)
    print("CONCLUSÃO:")
    print("A simulação realista mostra valores MUITO menores que a versão alucinada,")
    print("demonstrando o impacto da lógica de zona de impacto correta.")
    print("=" * 80)

if __name__ == "__main__":
    simular_lote1_realista()