# System Architecture

This document connects the constitutional layer of the Moral Money ecosystem to the technical implementation.

The system follows a layered structure.

Constitution
→ Principles
→ Community Model
→ Reputation Model
→ Blockchain Implementation


## Constitutional Layer

Defines the ethical and institutional rules of the ecosystem.

Documents:

- constitution.md
- principles.md
- community-model.md
- reputation-model.md


## Algorithmic Layer

Translates constitutional rules into mechanisms.

Examples:

- reputation calculation
- project lifecycle
- governance selection
- conflict resolution


## Blockchain Layer

The blockchain records and enforces system rules.

Responsibilities include:

- identity registration
- project records
- participation tracking
- reputation updates
- governance decisions


## Implementation

Implementation is organized through pallets.

Example:

pallets/reputation

Future pallets may include:

pallets/projects  
pallets/governance  
pallets/economy  


## Design Principle

The constitutional layer always governs the technical implementation.