# Error Tracker — Erros Frequentes e Histórico

Este diretório regista todos os erros de compilação que aparecem no projeto, organizados por frequência de ocorrência.

---

## 🤖 Automação

Este sistema está integrado com **GitHub Actions** para atualização automática:

### Como funciona:
1. Cada push/pull_request dispara o workflow `.github/workflows/build-and-track.yml`
2. Se houver erros de compilação, são extraídos automaticamente
3. Os erros são adicionados a `all-errors.md` com timestamp
4. Os erros frequentes (3+ ocorrências) são destacados no summary

### Para ativar localmente:
```bash
# Executar build e guardar log
cd blockchain-core && cargo build 2>&1 | tee /tmp/build.log

# Analisar erros
./scripts/parse-build-errors.sh /tmp/build.log ./docs/internal/error-tracker/
```

---

## 📊 FICHEIROS

| Ficheiro | Descrição |
|----------|-----------|
| `README.md` | Este ficheiro |
| `frequent-errors.md` | Erros que aparecem 3+ vezes |
| `all-errors.md` | Histórico completo de todos os erros |
| `resolved.md` | Erros resolvidos com soluções |
| `lessons-learned.md` | Regras e padrões do Polkadot SDK |
| `quick-reference.md` | Comandos e snippets úteis |
| `pre-commit-checklist.md` | Checklist antes de commit |
| `branch-history.md` | Histórico de branches |
| `links.md` | Links de referência |

---

## 🎯 COMO USAR

1. **Quando surgir um erro de compilação:**
   - Verificar primeiro `frequent-errors.md` para ver se já conhecemos o erro
   - Se for novo, adicionar a `all-errors.md`
   - Se aparecer 3+ vezes, mover para `frequent-errors.md`

2. **Quando um erro for resolvido:**
   - Mover para `resolved.md` com a solução documentada
   - Atualizar `frequent-errors.md` se necessário

3. **Revisão semanal:**
   - Analisar padrões de erros
   - Identificar causas raiz
   - Prevenir erros recorrentes

---

## 📈 MÉTRICAS

| Erro | Ocorrências | Última Vez | Status |
|------|-------------|------------|--------|
| (vazio) | — | — | — |

---

*Última atualização: 2026-03-20*
