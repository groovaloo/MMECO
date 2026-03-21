# Checklist Antes de Fazer Commit

## ✅ Runtime (runtime/src/lib.rs)

- [ ] `construct_runtime!` vem ANTES das implementações Config
- [ ] Type `Executive` usa `<` para generics: `Executive<Runtime, Block, ...>`
- [ ] Todos os pallets têm implementação `Config`
- [ ] `VERSION` tem `state_version: 1` (não `system_version`)

## ✅ Cargo.toml

- [ ] Todas as dependências usam `branch = "stable2412"` (não tags diferentes)
- [ ] `substrate-wasm-builder` está nas workspace dependencies
- [ ] Nomes de pallets consistentes (pallet-reputation, não reputation)

## ✅ Build Script (runtime/build.rs)
```rust
fn main() {
    substrate_wasm_builder::WasmBuilder::new()
        .with_current_project()
        .export_heap_base()
        .import_memory()
        .build();
}
```

## ✅ Workflow (.github/workflows/rust.yml)

- [ ] `cargo build --release -p mmeco-node` (não só `cargo build`)
- [ ] Rust 1.88.0 instalado
- [ ] `wasm32-unknown-unknown` target adicionado

---

*Última atualização: 2026-03-20*
