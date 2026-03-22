# Lições Aprendidas — Padrões e Regras do Polkadot SDK

## ⚠️ Regras de Ouro

### 1. Ordem de Construção do Runtime
**SEMPRE esta ordem:**
1. Imports básicos
2. Type aliases (Signature, AccountId, etc.)
3. `construct_runtime!` macro
4. Implementações `Config`
5. Type `Executive`
6. `impl_runtime_apis!`

**Por quê:** `construct_runtime!` gera tipos (RuntimeCall, RuntimeEvent) usados nas configs.

### 2. Sintaxe de Tipos Genéricos
```rust
// ❌ ERRADO
type Executive = SomeType
    Param1,
    Param2,
;

// ✅ CORRETO
type Executive = SomeType
    Param1,
    Param2,
>;
```

### 3. Versões do SDK
- `stable2412` → Branch estável (Dezembro 2024)
- `polkadot-stable2409` → Tag específica (Setembro 2024)
- **NUNCA usar `main`** → Muda diariamente, causa yanked dependencies

### 4. Vec vs BoundedVec
- Storage **SEMPRE** usa `BoundedVec<T, ConstU32<MAX>>`
- `Vec` só em parâmetros de funções ou memory

### 5. AccountId Ambiguity
Quando herda múltiplas traits com `AccountId`:
```rust
pub trait Config: frame_system::Config 
    + pallet_reputation::Config<AccountId = ::AccountId>
```

---

## 🔑 Soluções Rápidas para Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| E0432 import não encontrado | Pallets são crates separados | Usar `pallet_reputation::` com dependência no Cargo.toml |
| Vec não implementa MaxEncodedLen | FRAME exige tamanho fixo | Substituir por `BoundedVec<T, ConstU32<MAX>>` |
| BlockNumber.into() | Tipo genérico não converte | `block.try_into().unwrap_or(0u64)` |
| Versões diferentes frame-support | Multiple crate instances | Alinhar todos os Cargo.toml |
| AccountId ambíguo | Herança múltipla | Usar `T::AccountId` sem qualificação |

---

*Última atualização: 2026-03-20*

## Tipos e Traits

**Tipo:** category

**Data:** 2026-03-20

**Descrição:** Lição aprendida a partir de erros recorrentes

**Aplicação:** Aplicar este conhecimento em desenvolvimento futuro

---

## Sintaxe

**Tipo:** category

**Data:** 2026-03-21

**Descrição:** Lição aprendida a partir de erros recorrentes

**Aplicação:** Aplicar este conhecimento em desenvolvimento futuro

---

## Rust

**Tipo:** category

**Data:** 2026-03-22

**Descrição:** Lição aprendida a partir de erros recorrentes

**Aplicação:** Aplicar este conhecimento em desenvolvimento futuro

---

## Compilation

**Tipo:** category

**Data:** 2026-03-22

**Descrição:** Lição aprendida a partir de erros recorrentes

**Aplicação:** Aplicar este conhecimento em desenvolvimento futuro

---
