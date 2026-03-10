Moral Money – Reputation Algorithm

Overview

This document describes the computational model that implements the reputation system defined in reputation-system.md.

The algorithm converts participation in community projects into measurable reputation scores across multiple domains.


Core Variables

Each participant has a reputation vector.

Example:

R(user) = {
    construction: value,
    agriculture: value,
    energy: value,
    governance: value,
    health: value,
    logistics: value
}

Each value represents competence and trust level within that domain.


Project Contribution Model

Each project generates a contribution record.

Contribution = {
    user_id
    project_id
    domain
    role
    effort
    outcome
    feedback
}

These records form the basis for reputation calculation.


Reputation Update

After project completion, the system calculates a reputation change.

Example formula:

ΔR = BaseContribution × ImpactFactor × FeedbackScore

Where:

BaseContribution reflects participation level.
ImpactFactor reflects the importance of the project.
FeedbackScore reflects peer evaluation.


Reputation Decay

Reputation gradually decreases during long inactivity periods.

Example:

R(t) = R(t-1) × decay_factor

Decay should be slow and predictable.


Governance Selection

When governance is required in a domain:

1. The system ranks participants by reputation in that domain.
2. The top five are selected.
3. They form a temporary decision council.
4. After the decision, the council dissolves.


Anti-Manipulation Rules

The algorithm must detect and mitigate manipulation patterns.

Examples include:

- repeated mutual rating patterns
- sudden abnormal reputation spikes
- tightly connected evaluation clusters

Suspicious cases can be flagged for additional review.


Design Goal

The reputation algorithm must:

- reward real contribution
- recognize domain-specific competence
- prevent manipulation
- maintain fairness and transparency

