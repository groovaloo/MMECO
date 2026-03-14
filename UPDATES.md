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

---

## [2026-03-12] Expansão do pallet `projects` com fases dinâmicas

### Contexto
O pallet `projects` precisava de suportar fases dinâmicas com prova fotográfica (hash SHA-256), pagamentos por fase e validação por agentes IA, conforme a arquitectura do ecossistema Moral Money.

### Alterações Implementadas

**Novos tipos:**
- `PhaseStatus` — `Pending`, `InProgress`, `ProofSubmitted`, `Validated`, `Rejected`, `Paid`
- `Phase` — struct com `index`, `description`, `proof_hash: Option<[u8; 32]>`, `status`, `payment_amount`, `submitted_at`, `validated_at`, `paid_at`

**Novo storage:**
- `ProjectPhases: StorageDoubleMap<project_id, phase_index, Phase>` — fases dinâmicas por projecto

**Novos campos em `Project`:**
- `total_phases: u32` — número total de fases definidas
- `phases_completed: u32` — fases concluídas e validadas

**Novas extrinsics:**
- `add_phase` — agente IA adiciona fase ao projecto
- `submit_proof` — participante submete hash SHA-256 da foto
- `validate_phase` — agente IA valida a fase
- `reject_phase` — agente IA rejeita a fase
- `pay_phase` — regista pagamento de fase validada

### Erro encontrado durante escrita
**Causa:** O heredoc cortou o `<` nos StorageMap/StorageDoubleMap/StorageValue.

**Erro:**
```
error: expected one of `!`, `(`, `+`, `::`, `;`, `<`, or `where`, found reserved identifier `_`
```

**Solução:**
```bash
sed -i '' 's/= StorageMap$/= StorageMap</' pallets/projects/src/lib.rs
sed -i '' 's/= StorageDoubleMap$/= StorageDoubleMap</' pallets/projects/src/lib.rs
sed -i '' 's/= StorageValue$/= StorageValue</' pallets/projects/src/lib.rs
```

### Resultado
`cargo check -p pallet-projects` compila sem erros.

---

## [2026-03-12] Histórico completo de erros resolvidos pelo Opus

### Erro — unresolved import super::reputation
Pallets são crates independentes. Solução: adicionar dependência no Cargo.toml com package = "reputation" e importar com pallet_reputation::.

### Erro — Vec não implementa MaxEncodedLen
Substituir Vec por BoundedVec com limites ConstU32.

### Erro — block_number().into() mismatched types
Usar block.try_into().unwrap_or(0u64).

### Erro — Versões incompatíveis frame-support
Alinhar todos os Cargo.toml para usar a mesma fonte (substrate polkadot-v1.0.0).

### Erro — reputation::Pallet<Runtime> não implementa reputation::Config
No runtime usar type Reputation = Runtime (não o Pallet). No Config do pallet usar type Reputation: frame_system::Config + pallet_reputation::Config.

### Erro — pub use projects não encontra crate
Hífens tornam-se underscores: pub use pallet_projects.

### Erro — índices duplicados no Substrate polkadot-v1.0.0
Corrigir manualmente message.rs no cache com índices sequenciais 0-14.

### Erro — Rust 1.94 incompatível com polkadot-v1.0.0
Instalar e usar nightly-2023-12-01.

### Erro — Cargo.lock versão 4 incompatível com nightly-2023-12-01
Apagar Cargo.lock e usar stable para gerir dependências.

###

---

## [2026-03-13] Pallet `governance` — comissão temporária de conflitos

### Contexto
Novo pallet para gerir conflitos em projectos. Quando há um conflito, o pallet selecciona automaticamente os 5 membros com maior reputação no domínio do projecto (lendo directamente o storage do pallet reputation), regista a comissão na blockchain, recebe votos e dissolve-se após decisão por maioria.

### Estrutura implementada

**Tipos:**
- `DisputeStatus` — `Open`, `Decided`, `Cancelled`
- `Decision` — `ApproveProject`, `RejectProject`, `ApprovePhase`, `RejectPhase`
- `VoteChoice` — `Approve`, `Reject`
- `Vote<AccountId>` — membro, escolha, timestamp
- `Dispute<AccountId>` — id, project_id, phase_index, domain, council, votes, status, decision, reason, created_at, decided_at

**Storage:**
- `Disputes` — StorageMap dispute_id -> Dispute
- `DisputeCounter` — StorageValue contador
- `DisputesByProject` — StorageMap project_id -> BoundedVec de dispute_ids

**Extrinsics:**
- `raise_dispute(project_id, domain, phase_index, reason)` — cria disputa e selecciona comissão automaticamente via select_top_experts
- `submit_vote(dispute_id, choice)` — membro da comissão vota; maioria decide automaticamente
- `cancel_dispute(dispute_id)` — cancela disputa aberta

### Erros encontrados e resolvidos

**Erro 1 — heredoc corta `<` nos StorageMap/StorageValue/BoundedVec**
Solução:
```bash
sed -i '' 's/= StorageMap$/= StorageMap</' pallets/governance/src/lib.rs
sed -i '' 's/= StorageValue$/= StorageValue</' pallets/governance/src/lib.rs
sed -i '' 's/let mut council: BoundedVec$/let mut council: BoundedVec</' pallets/governance/src/lib.rs
```

**Erro 2 — AccountId ambíguo: `frame_system::Config::AccountId` vs `frame_system::pallet::Config::AccountId`**

Causa: Quando governance herda `frame_system::Config + pallet_reputation::Config`, o compilador vê dois `AccountId` diferentes porque `pallet_reputation::Config` herda de `frame_system::pallet::Config` (git) e o governance herda de `frame_system::Config` (crates.io). São o mesmo tipo em runtime mas o compilador não consegue unificá-los.

Solução — adicionar constraint que iguala os dois AccountId no bound do Config:
```rust
pub trait Config: frame_system::Config 
    + pallet_reputation::Config<AccountId = <Self as frame_system::Config>::AccountId> {
    type RuntimeEvent: ...
}
```
E usar sempre `<T as frame_system::Config>::AccountId` no código.

**Erro 3 — `pub use pallet::*` não encontra módulo**
Causa: O módulo chama-se `pallet` mas o compilador não o encontra sem o macro do frame.
Solução: Comentar a linha ou deixar o macro tratar da exportação.

### Resultado
`cargo check --workspace` compila sem erros. Apenas warnings de `trie-db` (terceiros) e `#[pallet::weight(10_000)]` deprecated (não bloqueante).

---

## [2026-03-13] Pallet governance integrado no runtime

### Alterações
- `runtime/Cargo.toml` — adicionado `pallet-governance` em dependencies e em `std` features
- `runtime/src/lib.rs` — adicionado `impl pallet_governance::Config for Runtime` e `Governance: pallet_governance` no `construct_runtime!`

### Erro final resolvido — AccountId ambíguo no pallet governance

**Causa raiz:**
`pallet_reputation::Config` herda apenas `frame_system::Config`. O `AccountId` é sempre `<T as frame_system::Config>::AccountId`. Tentar usar `<T as pallet_reputation::Config>::AccountId` causava `E0576: cannot find associated type AccountId in trait pallet_reputation::Config`.

**Solução definitiva:**
- Usar `T::AccountId` em todo o código do governance (sem qualificação explícita)
- Bound do Config: apenas `frame_system::Config + pallet_reputation::Config` sem constraints adicionais
- Não adicionar `where` clauses com `AccountId =` — causam recursão infinita (`E0275`)

### Resultado
`cargo check --workspace` compila sem erros.
