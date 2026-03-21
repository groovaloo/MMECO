# Quick Reference — Comandos e Snippets Úteis

## 🔍 Debugging no GitHub Actions
```bash
# Ver erros do último run
gh run view $(gh run list --limit 1 --json databaseId -q '.[0].databaseId') --log | grep -i error

# Ver run específico
gh run view 23342805238 --log | grep -i error

# Download do log completo
gh run view 23342805238 --log > build-log.txt
```

## 📦 Comandos Cargo Úteis
```bash
# Build só do runtime (mais rápido para testar)
cargo check -p mmeco-runtime

# Build completo local
cd blockchain-core
cargo build --release -p mmeco-node

# Ver dependências de um crate
cargo tree -p mmeco-runtime
```

## 🔧 Snippets de Configuração

### Config Mínimo de Pallet
```rust
impl pallet_name::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}
```

### Adicionar Novo Pallet ao Runtime
1. `Cargo.toml`:
```toml
pallet-new = { path = "../pallets/new", default-features = false }
```

2. `construct_runtime!`:
```rust
NewPallet: pallet_new = 8,
```

3. Config:
```rust
impl pallet_new::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}
```

---

## 📊 Comandos de Build

```bash
# Build debug (mais rápido, mas maior)
cargo build

# Build release (otimizado)
cargo build --release

# Apenas verificar sem compilar
cargo check

# Limpar cache
cargo clean
```

---

*Última atualização: 2026-03-20*

### type Executive = polkadot_sdk::frame_executive::Ex...

```rust
type Executive = polkadot_sdk::frame_executive::Executive
    Runtime,
    Block,
    polkadot_sdk::frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
;
```

**Uso:** Snippet de código para resolução de erros

---
