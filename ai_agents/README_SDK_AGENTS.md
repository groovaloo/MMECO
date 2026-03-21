# MMECO SDK Agents

Sistema de agentes para detecção automática de erros de compilação do SDK blockchain.

## 🚀 Visão Geral

O MMECO SDK Agents é um sistema avançado de detecção automática de erros que monitora builds, analisa erros de compilação e gera relatórios inteligentes. O sistema inclui:

- **📡 Keep-Alive Manager**: Mantém conexão ativa com GitHub (2 minutos)
- **🔍 Error Detector**: Monitora builds e detecta erros automaticamente
- **🧠 Memory Manager**: Sistema unificado de memória para soluções
- **🚨 Alert System**: Alertas inteligentes por múltiplos canais
- **📚 Documentation Manager**: Atualização automática de documentação
- **🌉 SDK DAO Bridge**: Integração com infraestrutura DAO existente

## 📁 Estrutura de Diretórios

```
ai_agents/
├── sdk_agents/                    # Agentes principais do SDK
│   ├── config.py                 # Configurações centralizadas
│   ├── keep_alive_manager.py     # Keep-alive inteligente
│   ├── error_detector.py         # Detector de erros
│   ├── memory_manager.py         # Memória unificada
│   ├── alert_system.py           # Sistema de alertas
│   └── documentation_manager.py  # Gestão de documentação
├── integration/                   # Integração entre sistemas
│   ├── sdk_dao_bridge.py         # Ponte SDK-DAO
│   └── unified_agent.py          # Agente unificado
├── legacy/                       # Agentes antigos (preservar)
│   ├── blockchain_error_agent.py
│   ├── rust_error_patterns.py
│   └── blockchain_memory.py
└── start_sdk_agents.py           # Script de inicialização
```

## ⚙️ Configuração

### Configurações Principais

As configurações estão centralizadas em `sdk_agents/config.py`:

```python
# Intervalos
keep_alive['interval_seconds'] = 120      # 2 minutos
error_monitoring['build_check_interval'] = 300  # 5 minutos

# Endpoints GitHub
keep_alive['endpoints'] = [
    'https://github.com',
    'https://api.github.com',
    'https://github.com/groovaloo/MMECO'
]

# Alertas
alerts['new_error_threshold'] = 5
alerts['channels'] = ['log', 'file', 'console']
```

### Variáveis de Ambiente

Para funcionalidades avançadas:

```bash
export GITHUB_TOKEN=seu_token_aqui
```

## 🚀 Uso

### Iniciar Sistema Completo

```bash
# Iniciar com configuração padrão
python ai_agents/start_sdk_agents.py

# Modo verboso
python ai_agents/start_sdk_agents.py --verbose

# Testar componentes sem iniciar loop
python ai_agents/start_sdk_agents.py --test
```

### Comandos Disponíveis

```bash
# Mostrar status do sistema
python ai_agents/start_sdk_agents.py --status

# Desativar componentes específicos
python ai_agents/start_sdk_agents.py --no-alerts --no-dao-bridge

# Ajuda completa
python ai_agents/start_sdk_agents.py --help
```

### Iniciar Agentes Individualmente

```bash
# Keep-Alive Manager
python ai_agents/sdk_agents/keep_alive_manager.py

# Error Detector
python ai_agents/sdk_agents/error_detector.py

# Memory Manager
python ai_agents/sdk_agents/memory_manager.py

# Alert System
python ai_agents/sdk_agents/alert_system.py

# Documentation Manager
python ai_agents/sdk_agents/documentation_manager.py

# SDK DAO Bridge
python ai_agents/integration/sdk_dao_bridge.py

# Unified Agent
python ai_agents/integration/unified_agent.py
```

## 📊 Monitoramento

### Status do Sistema

```bash
python ai_agents/start_sdk_agents.py --status
```

Saída:
```
🤖 UNIFIED AGENT STATUS
Status: running
Uptime: 3600.50s
Agents Started: 6
Agents Running: 6
Total Errors: 0
Total Alerts: 2

🔧 COMPONENTS:
  ✅ keep_alive: Running
  ✅ error_detector: Running
  ✅ memory_manager: Running
  ✅ alert_system: Running
  ✅ docs_manager: Running
  ✅ dao_bridge: Running
```

### Logs

Os logs são gerados em:

- `keep-alive-python.log` - Logs do keep-alive
- `sdk_agents.log` - Logs principais do sistema
- `alerts.log` - Logs de alertas
- `unified-agent-report-*.json` - Relatórios periódicos

## 🔍 Funcionalidades

### Keep-Alive Manager

- **Objetivo**: Manter conexão ativa com GitHub
- **Intervalo**: 2 minutos (configurável)
- **Endpoints**: GitHub, API GitHub, repositório específico
- **Monitoramento**: Saúde dos endpoints, falhas consecutivas
- **Alertas**: Falhas críticas, endpoints offline

### Error Detector

- **Objetivo**: Detectar erros de compilação automaticamente
- **Monitoramento**: Executa `cargo build` periodicamente
- **Análise**: Identifica tipos de erro, categorias, soluções
- **Memória**: Aprende com erros passados
- **Relatórios**: Diários, semanais, tendências

### Memory Manager

- **Objetivo**: Sistema unificado de memória para soluções
- **Fontes**: Erros detectados, base de conhecimento, histórico
- **Busca**: Similaridade, códigos de erro, categorias
- **Integração**: Error-tracker, documentação automática
- **Estatísticas**: Frequência, confiança, categorias

### Alert System

- **Objetivo**: Notificar sobre eventos críticos
- **Canais**: Log, arquivo, console, email, webhook
- **Regras**: Configuráveis por nível e condições
- **Cooldown**: Evita spam de alertas
- **Exportação**: Histórico de alertas

### Documentation Manager

- **Objetivo**: Atualizar documentação automaticamente
- **Arquivos**: all-errors.md, frequent-errors.md, resolved.md
- **Formato**: Markdown estruturado
- **Referências**: Comandos úteis, snippets de código
- **Relatórios**: Sumários periódicos

### SDK DAO Bridge

- **Objetivo**: Integrar com infraestrutura DAO existente
- **Sincronização**: Dados dos agentes para DAO
- **Eventos**: Comunicação entre sistemas
- **Estado**: Monitoramento da integração
- **Relatórios**: Sincronização periódica

## 🚨 Alertas

### Tipos de Alertas

1. **Info**: Informações gerais
2. **Warning**: Atenção necessária
3. **Critical**: Problema sério
4. **Emergency**: Falha crítica

### Condições de Disparo

- **Novos erros**: > 5 erros novos detectados
- **Falhas de build**: 3+ builds falhados consecutivos
- **Conectividade**: Falhas no GitHub
- **Tendências**: Aumento de 20% em erros
- **Memória**: Uso baixo de memória

### Canais de Alerta

- **Log**: Registro interno
- **Console**: Saída padrão
- **File**: Arquivo de logs
- **Email**: Notificação por email
- **Webhook**: Integração externa

## 📈 Relatórios

### Tipos de Relatórios

1. **Horário**: Status do sistema a cada hora
2. **Diário**: Resumo de erros e builds
3. **Semanal**: Tendências e estatísticas
4. **Sincronização**: Integração SDK-DAO

### Localização dos Relatórios

- `unified-agent-report-*.json` - Relatórios do agente unificado
- `error-report-*.json` - Relatórios de erros
- `sync-report-*.md` - Relatórios de sincronização
- `documentation-summary-*.md` - Resumos de documentação

## 🔗 Integração com DAO

### Componentes Legados Preservados

Os seguintes agentes legados são mantidos intactos:

- `blockchain_error_agent.py` - Agente de erros blockchain
- `rust_error_patterns.py` - Padrões de erros Rust
- `blockchain_memory.py` - Memória de erros blockchain

### Ponte de Integração

A `SDK DAO Bridge` permite:

- Compartilhar dados entre sistemas
- Sincronizar memória de erros
- Comunicar eventos importantes
- Manter compatibilidade com DAO

## 🛠️ Desenvolvimento

### Adicionar Novos Agentes

1. Criar agente em `sdk_agents/`
2. Implementar interface padrão
3. Conectar ao `Unified Agent`
4. Atualizar documentação

### Configurar Novas Regras de Alerta

```python
from sdk_agents.alert_system import AlertRule, AlertLevel, AlertChannel

rule = AlertRule(
    name="nova_regra",
    level=AlertLevel.WARNING,
    channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
    conditions={"type": "novo_evento", "threshold": 10},
    cooldown_minutes=5
)

alert_system.add_rule(rule)
```

### Extender Memory Manager

```python
from sdk_agents.memory_manager import MemoryManager

manager = MemoryManager()

# Aprender novo erro
manager.learn_error(
    error_msg="mensagem do erro",
    solution="solução aplicada",
    context="contexto do erro"
)

# Buscar solução
result = manager.search_solution("mensagem do erro")
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Keep-Alive não funciona**
   - Verificar conexão com internet
   - Checar endpoints configurados
   - Verificar logs de erro

2. **Error Detector não detecta erros**
   - Verificar caminho do projeto blockchain
   - Checar permissões de execução
   - Validar configuração do Cargo

3. **Alertas não são enviados**
   - Verificar configuração de canais
   - Checar regras de disparo
   - Validar cooldown

4. **Integração DAO falha**
   - Verificar conexão com DAO
   - Checar sincronização de dados
   - Validar formato de mensagens

### Logs de Depuração

```bash
# Modo verboso
python ai_agents/start_sdk_agents.py --verbose

# Logs específicos
tail -f sdk_agents.log
tail -f keep-alive-python.log
tail -f alerts.log
```

## 📝 Contribuição

### Diretrizes

1. **Testes**: Sempre testar novos agentes
2. **Documentação**: Atualizar README e docstrings
3. **Compatibilidade**: Manter compatibilidade com DAO
4. **Performance**: Otimizar loops e recursos

### Fluxo de Trabalho

1. Criar branch feature
2. Implementar agente
3. Testar localmente
4. Atualizar documentação
5. Criar PR

## 📄 Licença

Este projeto faz parte do ecossistema MMECO.

## 🤝 Suporte

Para suporte e dúvidas:

- Issues no repositório
- Documentação interna
- Comunidade DAO

---

**Nota**: Este sistema foi projetado para operar em conjunto com a infraestrutura DAO existente, mantendo total compatibilidade e permitindo evolução independente dos componentes.