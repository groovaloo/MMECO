# Branch History

| Branch | Objetivo | Resultado |
|--------|----------|-----------|
| bld-1.7 | Runtime clássico com construct_runtime! | 🟡 Em teste |
| bld-1.6 | Adicionar campos Config novos (stable2412) | ❌ Erro sintaxe Executive |
| bld-1.5 | Fix DoneSlashHandler + system_version | ❌ Faltavam campos Config |
| bld-1.4 | Usar TestDefaultConfig | ❌ DefaultConfig não existe |

---

## 📝 Notas sobre Branches

### bld-1.7 (Atual)
- Estado atual da branch principal
- Usa Polkadot SDK moderno com construct_runtime!
- Pallets: reputation, projects, governance
- Node com tokio + jsonrpsee

### bld-1.6
- Tentativa de adicionar novos campos Config
- Erro de sintaxe no Executive devido a formato antigo

### bld-1.5
- Problemas com handler e versão do sistema

### bld-1.4
- Tentativa de usar configuração padrão de testes
- Feature não existe no Polkadot SDK

---

*Última atualização: 2026-03-20*
