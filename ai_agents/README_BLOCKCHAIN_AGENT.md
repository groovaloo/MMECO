# Blockchain Error Agent

Agente de IA especializado em resolver erros de desenvolvimento blockchain (Rust/Substrate/Polkadot SDK).

## 📁 Ficheiros

| Ficheiro | Descrição |
|----------|-----------|
| `blockchain_error_agent.py` | Agente principal |
| `blockchain_memory.py` | Sistema de memória para erros |
| `rust_error_patterns.py` | Base de conhecimento de erros Rust |
| `test_blockchain_error_agent.py` | Testes unitários |
| `blockchain_errors_memory.json` | Memória persistente (criado automaticamente) |

## 🚀 Uso

### 1. Analisar erro específico

```bash
cd ai_agents
python blockchain_error_agent.py --error "error[E0277]: the trait bound..."

# Ou em modo verboso:
python blockchain_error_agent.py -e "error[E0432]: unresolved import" -v
```

### 2. Executar build e analisar erros

```bash
# Na raiz do projeto:
python ai_agents/blockchain_error_agent.py --build

# Projeto em caminho específico:
python ai_agents/blockchain_error_agent.py --build --project ./blockchain-core
```

### 3. Ver estatísticas

```bash
python blockchain_error_agent.py --stats
```

### 4. Modo interativo

```bash
python blockchain_error_agent.py --interactive
```

Comandos no modo interativo:
- `build` - Executar cargo build e analisar
- `stats` - Ver estatísticas
- `help` - Mostrar erros comuns do Substrate
- `quit` - Sair

### 5. Importar erros do error-tracker

```bash
python blockchain_error_agent.py --import-tracker
```

## 🎯 Funcionalidades

### Categorias de Erros Suportadas

- **Tipos e Traits** (E0277, E0283, E0308)
- **Imports e Módulos** (E0432, E0433)
- **Substrate Pallet** (Config, Storage, Events)
- **Storage** (StorageValue, StorageMap)
- **Sintaxe** (E0435, E0769)
- **Build/Linking** (wasm-opt, linking)

### Fluxo de Análise

```
1. Receber erro
2. Extrair código E0xxx
3. Identificar categorias
4. Procurar na memória local (JSON)
5. Se não encontrado, procurar na base de conhecimento
6. Retornar solução com nível de confiança
7. Guardar na memória para uso futuro
```

## 🔧 API Python

```python
from blockchain_error_agent import BlockchainErrorAgent

# Criar agente
agent = BlockchainErrorAgent()

# Analisar erro
result = agent.analyze_error("error[E0277]: the trait bound...")
print(result['solution'])

# Executar build
result = agent.analyze_build()
print(result['summary'])
```

## 📊 Exemplo de Output

```
============================================================
🔴 RELATÓRIO DE BUILD
============================================================

🔴 5 erros: 3 conhecidos, 2 novos

📊 ERROS POR CATEGORIA:

  Tipos e Traits: 2 erro(s)
  Imports e Módulos: 1 erro(s)
  Substrate Pallet: 2 erro(s)

------------------------------------------------------------
DETALHES DOS ERROS:
------------------------------------------------------------

1. E0277 @ pallets/governance/src/lib.rs:45
   the trait bound `Proposal: Encode` is not satisfied
   ✅ Solução disponível (60%)

2. E0432 @ runtime/src/lib.rs:12
   unresolved import `pallet_reputation`
   ✅ Solução disponível (95%)

...
```

## 🧪 Testes

```bash
cd ai_agents
python -m pytest test_blockchain_error_agent.py -v

# Ou usar unittest diretamente:
python test_blockchain_error_agent.py
```

## 🔄 Integração com CI/CD

O agente pode ser integrado com GitHub Actions:

```yaml
# .github/workflows/analyze-errors.yml
name: Analyze Build Errors
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Analyze build
        run: python ai_agents/blockchain_error_agent.py --build
```

## 📝 Notas

- A memória é guardada em `blockchain_errors_memory.json`
- Erros são aprendidos automaticamente durante builds
- Base de conhecimento inclui padrões específicos do Substrate
- Sistema é compatível com o `error-tracker` existente em `docs/internal/error-tracker/`

---

*Desenvolvido para o projeto MMECO*
