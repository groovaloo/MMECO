# Sistema de IA para Moral Money

## Visão Geral

Este repositório contém a implementação completa da inteligência artificial para o sistema Moral Money, baseado nos princípios de Equivalência Ética, Conselho dos 5, Governança Horizontal e P2P Offline.

## Arquitetura do Sistema

### Componentes Principais

1. **IA de Auditoria** (`ia_auditoria.py`)
   - Sistema de auditoria automática baseado em inteligência artificial
   - Integração com blockchain Substrate via RPC
   - Validação de contribuições reais vs. capital especulativo
   - Detecção de anomalias e fraudes

2. **Conselho dos 5** (`conselho_5.py`)
   - Sistema de governança horizontal baseado em reputação por domínio
   - Seleção automática de conselheiros
   - Votação ponderada por reputação
   - Decisões soberanas e imutáveis

3. **Equivalência Ética** (`equivalencia_etica.py`)
   - Implementação do princípio fundamental: Trabalho = Capital
   - Cálculo de equivalência entre trabalho e capital investido
   - Distribuição justa de Buildcoins baseada em mérito
   - Validação de contribuições reais

4. **Governança Horizontal** (`governanca_horizontal.py`)
   - Sistema de governança descentralizado
   - Propostas baseadas em expertise, não em poder econômico
   - Níveis de governança: Community, Domain, System, Constitutional
   - Transparência total e imparcialidade garantida

5. **P2P Offline** (`p2p_offline.py`)
   - Rede peer-to-peer para operação offline
   - Descoberta automática de nós na rede local
   - Sincronização segura de blockchain
   - Comunicação criptografada entre pares

6. **Integração Completa** (`integracao_completa.py`)
   - Coordenador de todos os componentes
   - Fluxo completo de operação do sistema
   - Monitoramento e estatísticas em tempo real

## Princípios Fundamentais

### Equivalência Ética
- **Princípio**: Trabalho = Capital
- **Exemplo**: Investidor de 60 anos com 4M€ = Trabalhador de 30 anos com 2000h de trabalho
- **Objetivo**: Distribuição justa baseada em contribuição real, não em capital inicial

### Conselho dos 5
- **Base**: Reputação por domínio de conhecimento
- **Soberania**: Decisões finais e imutáveis
- **Transparência**: Todas as decisões auditáveis na blockchain
- **Imparcialidade**: Seleção automática baseada em mérito

### Governança Horizontal
- **Descentralização**: Sem pontos de falha centralizados
- **Expertise**: Decisões baseadas em conhecimento, não em poder econômico
- **Participação**: Múltiplos níveis de governança
- **Resiliência**: Sistema operacional mesmo em condições adversas

### P2P Offline
- **Independência**: Operação sem dependência de internet
- **Resiliência**: Comunicação em ambientes hostis
- **Segurança**: Comunicação criptografada
- **Eficiência**: Sincronização inteligente de blockchain

## Instalação e Configuração

### Requisitos
- Python 3.8+
- Bibliotecas: requests, cryptography, aiohttp

### Instalação
```bash
pip install requests cryptography aiohttp
```

### Configuração
1. Configure o endpoint RPC do blockchain Substrate
2. Ajuste os parâmetros de rede P2P conforme necessário
3. Defina os níveis de reputação para cada domínio

## Uso

### Execução Individual de Componentes

```python
# IA de Auditoria
from ia_auditoria import MoralMoneyIA
ia = MoralMoneyIA()
report = ia.execute_audit(process_id=123)

# Conselho dos 5
from conselho_5 import ConselhoDos5
conselho = ConselhoDos5()
session = conselho.start_session(process_id=456, domain="Construction")

# Equivalência Ética
from equivalencia_etica import EquivalenciaEtica
equivalencia = EquivalenciaEtica()
calculation = equivalencia.calculate_ethical_equivalence(contribution)

# Governança Horizontal
from governanca_horizontal import GovernancaHorizontal
governanca = GovernancaHorizontal()
proposal_id = governanca.submit_proposal(...)

# P2P Offline
from p2p_offline import P2POffline
p2p = P2POffline("node_001", 8080)
p2p.start_network()
```

### Sistema Integrado
```python
from integracao_completa import SistemaIntegrado
import asyncio

async def main():
    sistema = SistemaIntegrado()
    await sistema.initialize_system()
    await sistema.start_main_loop()

asyncio.run(main())
```

## Exemplos de Uso

### Exemplo 1: Auditoria de Contribuição
```python
from equivalencia_etica import EthicalContribution, ContributionType

# Contribuição de trabalhador
worker = EthicalContribution(
    contributor_id="worker_001",
    contribution_type=ContributionType.CONSTRUCTION,
    work_hours=2000,
    skill_level=0.8,
    impact_factor=1.5,
    age=30,
    capital_invested=0.0,
    ethical_score=0.0
)

# Contribuição de investidor
investor = EthicalContribution(
    contributor_id="investor_001",
    contribution_type=ContributionType.CONSTRUCTION,
    work_hours=100,
    skill_level=0.9,
    impact_factor=1.2,
    age=60,
    capital_invested=4000000.0,
    ethical_score=0.0
)

# Validação de equivalência
equivalencia = EquivalenciaEtica()
worker_calc = equivalencia.calculate_ethical_equivalence(worker)
investor_calc = equivalencia.calculate_ethical_equivalence(investor)

print(f"Trabalhador: {worker_calc.buildcoin_allocation:.2f} Buildcoins")
print(f"Investidor: {investor_calc.buildcoin_allocation:.2f} Buildcoins")
print("Equivalência Ética implementada!")
```

### Exemplo 2: Proposta de Governança
```python
# Cria proposta constitucional
proposal_id = governanca.submit_proposal(
    proposer="expert_123",
    title="Emenda Constitucional: Equivalência Ética",
    description="Implementar o princípio de Equivalência Ética em todos os domínios",
    governance_level=GovernanceLevel.CONSTITUTIONAL,
    decision_type=DecisionType.AMENDMENT,
    required_quorum=0.75,
    required_majority=0.8
)

# Forma conselho constitucional
council = governanca.form_governance_council(proposal_id)

# Votação
for member in council:
    governanca.cast_governance_vote(proposal_id, member, "approve")

# Resultado
result, confidence, justification = governanca.calculate_governance_result(proposal_id)
print(f"Resultado: {result.value} (confiança: {confidence:.2f})")
```

## Integração com Blockchain

O sistema se integra com blockchain Substrate através de:

1. **RPC Calls**: Comunicação direta com o nó Substrate
2. **Pallets**: Integração com pallets de reputação e processos
3. **Event Listening**: Monitoramento de eventos em tempo real
4. **Transaction Broadcasting**: Emissão de transações de Buildcoin

### Endpoints RPC
- `reputation_selectTopExperts`: Seleção de especialistas
- `reputation_getReputation`: Consulta de reputação
- `processes_getProcess`: Obtenção de processos
- `processes_concluirProcesso`: Conclusão de processos

## Segurança

### Criptografia
- Comunicação P2P criptografada com Fernet
- Assinatura digital de transações
- Verificação de integridade de dados

### Validação
- Verificação de reputação para todas as operações
- Validação de contribuições reais vs. especulação
- Auditoria automática de anomalias

### Resiliência
- Operação offline independente
- Redundância de nós na rede P2P
- Recuperação automática de falhas

## Monitoramento e Estatísticas

### Métricas Disponíveis
- Altura do blockchain sincronizado
- Número de peers ativos
- Taxa de contribuições éticas validadas
- Distribuição de Buildcoins por domínio
- Tempo de resposta da IA de auditoria

### Logs
- Auditoria detalhada de todas as operações
- Monitoramento de saúde do sistema
- Alertas de anomalias e falhas

## Contribuição

### Diretrizes de Desenvolvimento
1. Mantenha a compatibilidade com Substrate
2. Siga os princípios de Equivalência Ética
3. Implemente testes para novas funcionalidades
4. Documente todas as mudanças

### Testes
```bash
# Testes unitários
python -m pytest tests/

# Testes de integração
python -m pytest tests/integration/

# Testes de performance
python -m pytest tests/performance/
```

## Licença

Este projeto está licenciado sob os termos da licença MIT.

## Contato

Para suporte e contribuições:
- Email: support@moralmoney.org
- Discord: [Moral Money Community](https://discord.gg/moralmoney)
- GitHub Issues: [Reportar Problemas](https://github.com/moralmoney/ai-system/issues)

## Agradecimentos

Este sistema é baseado nos princípios filosóficos de:
- Equivalência Ética: Trabalho = Capital
- Governança Horizontal: Decisões baseadas em expertise
- Soberania do Conselho dos 5: Imparcialidade e transparência
- Resiliência P2P: Independência e operação offline