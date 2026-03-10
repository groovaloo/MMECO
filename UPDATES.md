# Project Updates

## 2026-03

- Initial repository cleanup
- Removal of duplicated documentation
- Creation of constitutional documentation hierarchy
- Basic Substrate project structure created

## 2026-03-09 — Repository cleanup and documentation structure

### Problem
The repository accumulated duplicated documentation in two locations:

docs/
blockchain-core/docs/

This created confusion about which documents were authoritative.

### Resolution
Removed the duplicated documentation inside:

blockchain-core/docs

All institutional documentation now lives exclusively in:

docs/

### Constitutional hierarchy created

docs/constitution/

- constitution.md
- principles.md
- community-model.md
- reputation-model.md
- architecture.md

This establishes the rule:

Constitution → System Model → Algorithms → Blockchain Implementation

### Additional cleanup

Removed empty files:

- economia.md
- governanca.md
- manifesto.md

Added initial content to:

- README.md
- UPDATES.md

### Result

Clean repository structure:

ai-agents/
blockchain-core/
docs/
frontend/
scripts/

Documentation hierarchy is now consistent and non-duplicated.

## 2026-03-10 — Substrate Dependencies Compatibility Issues

### Problem
The project encountered critical dependency conflicts in the Substrate blockchain implementation:

- **frame_metadata_enabled error**: Indicated incompatible versions between sp-api, sp-runtime, and frame-support dependencies
- **Version incompatibilities**: Different Cargo.toml files used conflicting Substrate versions (34.0.0, 35.0.0, 38.0.0, 39.0.0)
- **Yanked versions**: Multiple attempts failed because versions 34.0.0, 33.0.0, 32.0.0, and 27.0.0 were marked as yanked on crates.io
- **Missing versions**: sc-rpc-server versions 0.35.0, 0.34.0, 0.33.0, 0.32.0 do not exist in crates.io

### Dependencies analyzed

**blockchain-core/runtime/Cargo.toml:**
- frame-support: 38.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- frame-system: 38.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-runtime: 39.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-api: 34.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-core: 34.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-version: 37.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0

**blockchain-core/node/Cargo.toml:**
- sc-cli: 0.36.0 → 0.34.0 → 0.35.0 → 0.34.0 → 0.33.0 → 0.32.0 → 0.27.0
- sc-service: 0.35.0 → 0.34.0 → 0.35.0 → 0.34.0 → 0.33.0 → 0.32.0 → 0.27.0
- sc-network: 0.34.0 → 0.34.0 → 0.35.0 → 0.34.0 → 0.33.0 → 0.32.0 → 0.27.0
- sc-rpc-server: 15.0.0 → 0.34.0 → 0.35.0 → 0.34.0 → 0.33.0 → 0.32.0 → 0.27.0
- sp-core: 28.0.0 → 34.0.0 → 35.0.0 → 34.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-runtime: 30.0.0 → 34.0.0 → 35.0.0 → 34.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-api: 26.0.0 → 34.0.0 → 35.0.0 → 34.0.0 → 33.0.0 → 32.0.0 → 27.0.0

**blockchain-core/pallets/reputation/Cargo.toml:**
- frame-support: 38.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- frame-system: 38.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-std: 14.0.0 (consistent)
- sp-core: 34.0.0 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-runtime: 39.0.5 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0
- sp-io: 38.0.2 → 34.0.0 → 35.0.0 → 33.0.0 → 32.0.0 → 27.0.0

### Attempts to resolve

1. **Initial compatibility fix**: Standardized all dependencies to version 34.0.0
2. **Version updates**: Progressively tried newer versions (35.0.0, 33.0.0, 32.0.0, 27.0.0)
3. **Fixed version syntax**: Applied strict version pinning with = syntax for P2P offline compatibility
4. **Vendor configuration**: Created .cargo/config.toml for cargo vendor support

### Current status

All Cargo.toml files have been updated with:
- Fixed version syntax (e.g., "=27.0.0")
- Consistent version numbers across all files
- Vendor configuration for offline compilation

However, the project still cannot compile due to:
- Version 27.0.0 being yanked from crates.io
- Missing sc-rpc-server versions in the 0.27.0 range

### Next steps required

1. **Research available versions**: Identify which Substrate versions are actually available and not yanked
2. **Use git dependencies**: Consider using git dependencies pointing to specific commits for stability
3. **Alternative approach**: Consider using a different Substrate version range that is stable and available
4. **Test compilation**: Once compatible versions are identified, test cargo build --release

### Files modified

- blockchain-core/runtime/Cargo.toml
- blockchain-core/node/Cargo.toml  
- blockchain-core/pallets/reputation/Cargo.toml
- blockchain-core/.cargo/config.toml (created)

### Impact

This dependency issue prevents the Moral Money blockchain from compiling and running, blocking all development and testing activities. The project requires stable, compatible Substrate dependencies to proceed.

## 2026-03-10 — Substrate Dependency Resolution

### Problem resolved

The `cargo build` failure was caused by three compounding issues:

1. **Yanked versions**: Versions 27.0.0–34.0.0 of `frame-support`, `frame-system`, `sp-runtime` etc. were yanked from crates.io
2. **Vendor override blocking network**: `.cargo/config.toml` forced offline vendor mode, preventing resolution of any registry dependencies
3. **Missing `frame_system::Config` associated types**: Newer versions added `SingleBlockMigrations`, `MultiBlockMigrator`, `PreInherents`, `PostInherents`, `PostTransactions`

### Resolution

**Files modified:**

- `.cargo/config.toml` — removed vendor override; now uses crates.io directly
- `Cargo.toml` (workspace) — added `[patch.crates-io]` section pointing to `polkadot-stable2412` git tag for future use
- `pallets/reputation/Cargo.toml` — updated to compatible versions (frame-support 38.0.0, sp-runtime 39.0.0, sp-io 38.0.0)
- `runtime/Cargo.toml` — updated to compatible versions (frame-support 38.0.0, sp-api 34.0.0, sp-core 34.0.0, sp-version 37.0.0)
- `node/Cargo.toml` — removed unused sc-cli, sc-service, sc-network, sc-rpc-server, sp-api, sp-api-proc-macro, futures, serde, hyper dependencies (none used in main.rs)
- `runtime/src/lib.rs` — added 5 missing associated types to `frame_system::Config` impl; fixed `RuntimeVersion` declaration and type aliases for `Block`, `Header`, `UncheckedExtrinsic`
- `node/src/main.rs` — removed unused `sp_runtime` import

### Result

`cargo build` completes successfully with only deprecation warnings (constant weights) that are non-blocking.
