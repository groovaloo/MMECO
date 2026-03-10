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