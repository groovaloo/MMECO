# UPDATES — Registo de Erros e Soluções

---

## [2026-03-11] Integração do pallet `projects` com `reputation`

### Contexto
O pallet `pallet-projects` precisava importar tipos (`ContributionType`, `SubContributionType`) do pallet `reputation` e referenciar o seu `Config` trait. O projeto não compilava com vários erros encadeados.

---

### Erro 1 — `E0432`/`E0433`: unresolved import `super::reputation`

**Ficheiros:** `pallets/projects/src/lib.rs`

**Causa:**
Em Substrate, pallets são crates independentes. `super::reputation` não existe porque `reputation` não é um módulo filho de `projects` — é uma crate separada. As tentativas com `crate::reputation` e `self::reputation` falham pelo mesmo motivo.

**Solução:**
1. Adicionar o pallet como dependência no `Cargo.toml` do projects:
   ```toml
   pallet-reputation = { package = "reputation", path = "../reputation", default-features = false }
   ```
   O `package = "reputation"` é necessário porque o nome do crate em `Cargo.toml` do reputation é `reputation`, mas queremos referenciá-lo como `pallet-reputation` (convenção Substrate).

2. Importar no `lib.rs` usando o nome do crate com underscore:
   ```rust
   pub use pallet_reputation::pallet::{ContributionType, SubContributionType};
   ```

3. Adicionar ao workspace em `blockchain-core/Cargo.toml`:
   ```toml
   "pallets/projects",
   ```

---

### Erro 2 — `E0277`: `Vec<u8>`, `Vec<AccountId>`, `Vec<u64>` não implementam `MaxEncodedLen`

**Ficheiros:** `pallets/projects/src/lib.rs`

**Causa:**
O FRAME exige que todos os tipos em storage implementem `MaxEncodedLen`. `Vec` tem tamanho dinâmico e não pode satisfazer este trait. As structs `Project` e `ProjectParticipant` tinham `#[derive(MaxEncodedLen)]` mas usavam `Vec`.

**Solução:**
Substituir todos os `Vec` por `BoundedVec` com limites definidos como constantes:
```rust
pub const MAX_NAME_LEN: u32 = 100;
pub const MAX_DESC_LEN: u32 = 500;
pub const MAX_PARTICIPANTS: u32 = 256;
pub const MAX_PROJECTS_PER_STATUS: u32 = 10_000;

// Nas structs:
pub name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
pub description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
pub participants: BoundedVec<AccountId, ConstU32<MAX_PARTICIPANTS>>,

// No storage ProjectsByStatus:
BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>>
```

Os parâmetros das extrinsics também passam a receber `BoundedVec` diretamente.
Para inserir numa `BoundedVec` usa-se `try_push(...).map_err(|_| Error::<T>::TooManyX)?`.

---

### Erro 3 — `E0308`: mismatched types em `block_number().into()`

**Ficheiros:** `pallets/projects/src/lib.rs`

**Causa:**
`<frame_system::Pallet<T>>::block_number()` retorna `BlockNumberFor<T>`, que é um tipo genérico. Não converte diretamente para `u64` com `.into()` porque o compilador não pode garantir que `BlockNumberFor<T>: Into<u64>`.

**Solução:**
```rust
let block = <frame_system::Pallet<T>>::block_number();
let created_at: u64 = block.try_into().unwrap_or(0u64);
```
`TryInto<u64>` está implementado para os tipos numéricos comuns usados como BlockNumber.

---

### Erro 4 — Versões incompatíveis de `frame-support` (duas instâncias do mesmo crate)

**Ficheiros:** `pallets/projects/Cargo.toml`

**Causa:**
O pallet `projects` usava `frame-support 34.0.0` enquanto o `reputation` e o `runtime` usavam `38.x`. Em Rust, versões diferentes do mesmo crate são tipos completamente distintos — os traits de uma versão não são satisfeitos pelos tipos da outra. O erro manifestava-se como `Runtime: frame_system::pallet::Config` not satisfied.

**Solução:**
Alinhar todas as versões do `projects/Cargo.toml` com as usadas no `reputation` e no `runtime`:
```toml
frame-support = { version = "38.0.0", default-features = false }
frame-system  = { version = "38.0.0", default-features = false }
sp-runtime    = { version = "39.0.0", default-features = false }
sp-io         = { version = "38.0.0", default-features = false }
```

---

### Erro 5 — `E0277`: `reputation::Pallet<Runtime>` não implementa `reputation::Config`

**Ficheiros:** `runtime/src/lib.rs`, `pallets/projects/src/lib.rs`

**Causa:**
No runtime estava configurado `type Reputation = Reputation`, onde `Reputation` é o alias para `reputation::Pallet<Runtime>` gerado pelo `construct_runtime!`. Mas o bound no Config do pallet projects exigia `pallet_reputation::Config`, que está implementado para `Runtime`, não para `reputation::Pallet<Runtime>`.

**Solução em dois passos:**

1. No `lib.rs` do projects, o bound do associated type deve incluir `frame_system::Config`:
   ```rust
   type Reputation: frame_system::Config + pallet_reputation::Config;
   ```

2. No `runtime/src/lib.rs`, passar `Runtime` (que implementa o Config) em vez do Pallet:
   ```rust
   impl pallet_projects::Config for Runtime {
       type RuntimeEvent = RuntimeEvent;
       type Reputation = Runtime;  // não "Reputation" (que é o Pallet)
   }
   ```

---

### Erro 6 — `pub use projects` no runtime não encontra o crate

**Ficheiros:** `runtime/src/lib.rs`

**Causa:**
O crate chama-se `pallet-projects` (com hífen). Em Rust, hífens tornam-se underscores no código. `pub use projects` procurava um crate chamado `projects` que não existe.

**Solução:**
```rust
// Errado:
pub use projects;

// Correto:
pub use pallet_projects;

// E no construct_runtime!:
Projects: pallet_projects,

// E no impl:
impl pallet_projects::Config for Runtime { ... }
```

---

### Resultado Final
Workspace inteiro compila sem erros (`cargo check --workspace`). Apenas warnings em crates de terceiros (`trie-db`) não relacionados com o projeto.
