#!/usr/bin/env python3
"""
Simulação Moral Money - Ecossistema Completo
"""

import hashlib
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from local_ledger import Blockchain, Transaction, TransactionType


class ContributionType(Enum):
    CONSTRUCTION = "Construction"
    AGRICULTURE  = "Agriculture"
    ENERGY       = "Energy"
    GOVERNANCE   = "Governance"
    HEALTH       = "Health"
    LOGISTICS    = "Logistics"

class ProjectStatus(Enum):
    CREATED   = "Created"
    ACTIVE    = "Active"
    COMPLETED = "Completed"
    EVALUATED = "Evaluated"
    CANCELLED = "Cancelled"

class PhaseStatus(Enum):
    PENDING         = "Pending"
    IN_PROGRESS     = "InProgress"
    PROOF_SUBMITTED = "ProofSubmitted"
    VALIDATED       = "Validated"
    REJECTED        = "Rejected"
    PAID            = "Paid"

class DisputeStatus(Enum):
    OPEN      = "Open"
    DECIDED   = "Decided"
    CANCELLED = "Cancelled"

class VoteChoice(Enum):
    APPROVE = "Approve"
    REJECT  = "Reject"


@dataclass
class Member:
    id: str
    name: str
    domain: ContributionType
    reputation: Dict[str, int] = field(default_factory=dict)
    buildcoin: float = 0.0

    def total_reputation(self) -> int:
        return sum(self.reputation.values())

    def domain_reputation(self) -> int:
        return self.reputation.get(self.domain.value, 0)


@dataclass
class Phase:
    index: int
    description: str
    payment_amount: float
    status: PhaseStatus = PhaseStatus.PENDING
    proof_hash: Optional[str] = None
    submitted_at: Optional[float] = None
    validated_at: Optional[float] = None
    paid_at: Optional[float] = None


@dataclass
class Project:
    id: int
    name: str
    description: str
    domain: ContributionType
    creator_id: str
    status: ProjectStatus = ProjectStatus.CREATED
    participants: List[str] = field(default_factory=list)
    phases: List[Phase] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


@dataclass
class Vote:
    member_id: str
    choice: VoteChoice
    voted_at: float = field(default_factory=time.time)


@dataclass
class Dispute:
    id: int
    project_id: int
    domain: ContributionType
    reason: str
    council: List[str]
    votes: List[Vote] = field(default_factory=list)
    status: DisputeStatus = DisputeStatus.OPEN
    decision: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    decided_at: Optional[float] = None


class MoralMoneyLedger:

    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.members: Dict[str, Member] = {}
        self.projects: Dict[int, Project] = {}
        self.disputes: Dict[int, Dispute] = {}
        self._project_counter = 0
        self._dispute_counter = 0

    def register_member(self, member: Member):
        self.members[member.id] = member
        self._record("Sistema", member.id, 0,
                     f"Registo: {member.name} | {member.domain.value}",
                     TransactionType.PAYMENT)

    def record_contribution(self, member_id: str, domain: ContributionType, amount: int):
        member = self.members.get(member_id)
        if not member:
            return
        member.reputation[domain.value] = member.reputation.get(domain.value, 0) + amount
        self._record(member_id, "Reputation", amount,
                     f"record_contribution | {domain.value} | +{amount}",
                     TransactionType.PAYMENT)
        print(f"  REPUTACAO {member.name} +{amount} em {domain.value} (total: {member.reputation[domain.value]})")

    def issue_buildcoin(self, member_id: str, amount: float, reason: str):
        member = self.members.get(member_id)
        if not member:
            return
        member.buildcoin += amount
        self._record("Sistema", member_id, amount,
                     f"issue_buildcoin | {reason}",
                     TransactionType.PAYMENT)
        print(f"  BUILDCOIN {member.name} +{amount:.2f} BLD | {reason}")

    def select_top_experts(self, domain: ContributionType, n: int = 5) -> List[Member]:
        candidates = [m for m in self.members.values() if m.domain == domain]
        candidates.sort(key=lambda m: m.reputation.get(domain.value, 0), reverse=True)
        return candidates[:n]

    def create_project(self, creator_id: str, name: str, description: str,
                       domain: ContributionType) -> Project:
        self._project_counter += 1
        project = Project(id=self._project_counter, name=name,
                          description=description, domain=domain,
                          creator_id=creator_id, participants=[creator_id])
        self.projects[project.id] = project
        self._record(creator_id, "Projects", 0,
                     f"create_project | id:{project.id} | {name} | {domain.value}",
                     TransactionType.PAYMENT)
        print(f"\nPROJECTO [{project.id}] {name} ({domain.value})")
        return project

    def add_phase(self, project_id: int, description: str, payment_amount: float) -> Optional[Phase]:
        project = self.projects.get(project_id)
        if not project:
            return None
        phase = Phase(index=len(project.phases), description=description,
                      payment_amount=payment_amount)
        project.phases.append(phase)
        project.status = ProjectStatus.ACTIVE
        self._record("Sistema", f"project_{project_id}", payment_amount,
                     f"add_phase | proj:{project_id} | fase:{phase.index} | {description}",
                     TransactionType.PAYMENT)
        print(f"  FASE {phase.index}: {description} ({payment_amount:.2f} BLD)")
        return phase

    def submit_proof(self, project_id: int, phase_index: int, photo_data: str) -> Optional[str]:
        project = self.projects.get(project_id)
        if not project or phase_index >= len(project.phases):
            return None
        phase = project.phases[phase_index]
        proof_hash = hashlib.sha256(photo_data.encode()).hexdigest()
        phase.proof_hash = proof_hash
        phase.status = PhaseStatus.PROOF_SUBMITTED
        phase.submitted_at = time.time()
        self._record(project.creator_id, f"project_{project_id}", 0,
                     f"submit_proof | proj:{project_id} fase:{phase_index} hash:{proof_hash[:16]}...",
                     TransactionType.PAYMENT)
        print(f"  PROVA proj:{project_id} fase:{phase_index} hash:{proof_hash[:16]}...")
        return proof_hash

    def validate_phase(self, project_id: int, phase_index: int, validator_id: str) -> bool:
        project = self.projects.get(project_id)
        if not project or phase_index >= len(project.phases):
            return False
        phase = project.phases[phase_index]
        if phase.status != PhaseStatus.PROOF_SUBMITTED:
            return False
        phase.status = PhaseStatus.VALIDATED
        phase.validated_at = time.time()
        self._record(validator_id, f"project_{project_id}", 0,
                     f"validate_phase | proj:{project_id} fase:{phase_index}",
                     TransactionType.PAYMENT)
        print(f"  VALIDADO proj:{project_id} fase:{phase_index} por {validator_id}")
        return True

    def pay_phase(self, project_id: int, phase_index: int) -> bool:
        project = self.projects.get(project_id)
        if not project or phase_index >= len(project.phases):
            return False
        phase = project.phases[phase_index]
        if phase.status != PhaseStatus.VALIDATED:
            return False
        phase.status = PhaseStatus.PAID
        phase.paid_at = time.time()
        self.issue_buildcoin(project.creator_id, phase.payment_amount,
                             f"fase {phase_index} proj {project_id}")
        return True

    def raise_dispute(self, project_id: int, reason: str) -> Optional[Dispute]:
        project = self.projects.get(project_id)
        if not project:
            return None
        experts = self.select_top_experts(project.domain, 5)
        if len(experts) < 3:
            print(f"  ERRO: especialistas insuficientes em {project.domain.value}")
            return None
        council_ids = [e.id for e in experts]
        self._dispute_counter += 1
        dispute = Dispute(id=self._dispute_counter, project_id=project_id,
                          domain=project.domain, reason=reason, council=council_ids)
        self.disputes[dispute.id] = dispute
        self._record("Sistema", "Governance", 0,
                     f"raise_dispute | disputa:{dispute.id} proj:{project_id} | {reason}",
                     TransactionType.VOTE)
        print(f"\nDISPUTA #{dispute.id} proj:{project_id}")
        print(f"  Razao: {reason}")
        print(f"  Comissao: {', '.join(council_ids)}")
        return dispute

    def submit_vote(self, dispute_id: int, member_id: str, choice: VoteChoice) -> bool:
        dispute = self.disputes.get(dispute_id)
        if not dispute or dispute.status != DisputeStatus.OPEN:
            return False
        if member_id not in dispute.council:
            return False
        if any(v.member_id == member_id for v in dispute.votes):
            return False
        dispute.votes.append(Vote(member_id=member_id, choice=choice))
        self._record(member_id, "Governance", 0,
                     f"submit_vote | disputa:{dispute_id} | {choice.value}",
                     TransactionType.VOTE)
        print(f"  VOTO {member_id}: {choice.value}")
        approve = sum(1 for v in dispute.votes if v.choice == VoteChoice.APPROVE)
        reject  = sum(1 for v in dispute.votes if v.choice == VoteChoice.REJECT)
        majority = (len(dispute.council) // 2) + 1
        if approve >= majority:
            self._resolve_dispute(dispute, "ApproveProject")
        elif reject >= majority:
            self._resolve_dispute(dispute, "RejectProject")
        return True

    def _resolve_dispute(self, dispute: Dispute, decision: str):
        dispute.status = DisputeStatus.DECIDED
        dispute.decision = decision
        dispute.decided_at = time.time()
        self._record("Governance", "Sistema", 0,
                     f"dispute_decided | disputa:{dispute.id} | {decision}",
                     TransactionType.VOTE)
        emoji = "APROVADO" if decision == "ApproveProject" else "REJEITADO"
        print(f"\n  DECISAO disputa #{dispute.id}: {emoji}")
        print(f"  Comissao dissolvida.")

    def print_report(self):
        print("\n" + "="*70)
        print("RELATORIO MORAL MONEY LEDGER")
        print("="*70)
        print(f"\nMEMBROS ({len(self.members)})")
        for m in sorted(self.members.values(),
                        key=lambda x: x.total_reputation(), reverse=True):
            print(f"  {m.name:20s} | {m.domain.value:15s} | "
                  f"rep:{m.total_reputation():5d} | BLD:{m.buildcoin:8.2f}")
        print(f"\nPROJECTOS ({len(self.projects)})")
        for p in self.projects.values():
            pagas = sum(1 for f in p.phases if f.status == PhaseStatus.PAID)
            print(f"  [{p.id}] {p.name:30s} | {p.status.value:10s} | fases:{pagas}/{len(p.phases)}")
        print(f"\nDISPUTAS ({len(self.disputes)})")
        for d in self.disputes.values():
            print(f"  #{d.id} proj:{d.project_id} | {d.status.value} | {d.decision or 'pendente'}")
        print(f"\nBLOCKCHAIN")
        print(f"  Blocos: {len(self.blockchain.chain)}")
        print(f"  Mempool: {len(self.blockchain.mempool)}")
        print("="*70)

    def _record(self, sender, receiver, amount, description, tx_type):
        self.blockchain.add_transaction(Transaction(
            sender=sender, receiver=receiver, amount=amount,
            transaction_type=tx_type, description=description,
            timestamp=time.time()
        ))


def run_simulation():
    print("SIMULACAO MORAL MONEY")
    print("="*70)

    blockchain = Blockchain(difficulty=1)
    blockchain.start_mining(interval=3)
    ledger = MoralMoneyLedger(blockchain)

    print("\nA registar membros...")
    members_data = [
        ("nuno",      "Nuno Cunha",      ContributionType.CONSTRUCTION),
        ("joao",      "Joao Silva",      ContributionType.CONSTRUCTION),
        ("pedro",     "Pedro Costa",     ContributionType.CONSTRUCTION),
        ("manuel",    "Manuel Ferreira", ContributionType.CONSTRUCTION),
        ("antonio",   "Antonio Sousa",   ContributionType.CONSTRUCTION),
        ("carlos",    "Carlos Lopes",    ContributionType.CONSTRUCTION),
        ("maria",     "Maria Santos",    ContributionType.AGRICULTURE),
        ("ana",       "Ana Oliveira",    ContributionType.AGRICULTURE),
        ("isabel",    "Isabel Martins",  ContributionType.AGRICULTURE),
        ("teresa",    "Teresa Alves",    ContributionType.AGRICULTURE),
        ("rosa",      "Rosa Pereira",    ContributionType.AGRICULTURE),
        ("dr_jose",   "Dr Jose Matos",   ContributionType.HEALTH),
        ("enf_paula", "Enf Paula Dias",  ContributionType.HEALTH),
        ("dr_luis",   "Dr Luis Ramos",   ContributionType.HEALTH),
        ("paulo",     "Paulo Neves",     ContributionType.ENERGY),
        ("rui",       "Rui Carvalho",    ContributionType.ENERGY),
        ("sergio",    "Sergio Batista",  ContributionType.ENERGY),
        ("miguel",    "Miguel Torres",   ContributionType.LOGISTICS),
        ("tiago",     "Tiago Gomes",     ContributionType.LOGISTICS),
        ("helena",    "Helena Cruz",     ContributionType.GOVERNANCE),
        ("fatima",    "Fatima Mendes",   ContributionType.GOVERNANCE),
    ]
    for mid, name, domain in members_data:
        ledger.register_member(Member(id=mid, name=name, domain=domain))

    print("\nA registar contribuicoes...")
    contributions = [
        ("nuno",      ContributionType.CONSTRUCTION, 850),
        ("joao",      ContributionType.CONSTRUCTION, 620),
        ("pedro",     ContributionType.CONSTRUCTION, 580),
        ("manuel",    ContributionType.CONSTRUCTION, 490),
        ("antonio",   ContributionType.CONSTRUCTION, 430),
        ("carlos",    ContributionType.CONSTRUCTION, 310),
        ("maria",     ContributionType.AGRICULTURE,  760),
        ("ana",       ContributionType.AGRICULTURE,  640),
        ("isabel",    ContributionType.AGRICULTURE,  520),
        ("teresa",    ContributionType.AGRICULTURE,  480),
        ("rosa",      ContributionType.AGRICULTURE,  350),
        ("dr_jose",   ContributionType.HEALTH,       900),
        ("enf_paula", ContributionType.HEALTH,       650),
        ("dr_luis",   ContributionType.HEALTH,       580),
        ("paulo",     ContributionType.ENERGY,       700),
        ("rui",       ContributionType.ENERGY,       550),
        ("sergio",    ContributionType.ENERGY,       420),
        ("miguel",    ContributionType.LOGISTICS,    600),
        ("tiago",     ContributionType.LOGISTICS,    480),
        ("helena",    ContributionType.GOVERNANCE,   820),
        ("fatima",    ContributionType.GOVERNANCE,   710),
    ]
    for mid, domain, amount in contributions:
        ledger.record_contribution(mid, domain, amount)

    print("\nA criar projecto de construcao...")
    proj = ledger.create_project("nuno", "Casa Modular LSF Lote 3",
                                 "Habitacao modular LSF familia Silva",
                                 ContributionType.CONSTRUCTION)
    ledger.add_phase(proj.id, "Fundacoes e laje", 500.0)
    ledger.add_phase(proj.id, "Estrutura LSF",    800.0)
    ledger.add_phase(proj.id, "Cobertura",        400.0)
    ledger.add_phase(proj.id, "Instalacoes",      350.0)

    print("\nA submeter provas e validar fases...")
    ledger.submit_proof(proj.id, 0, f"foto_fundacoes_{time.time()}_gps_39.4153_-9.1345")
    ledger.validate_phase(proj.id, 0, "dr_jose")
    ledger.pay_phase(proj.id, 0)

    ledger.submit_proof(proj.id, 1, f"foto_estrutura_{time.time()}_gps_39.4153_-9.1345")
    ledger.validate_phase(proj.id, 1, "helena")
    ledger.pay_phase(proj.id, 1)

    ledger.submit_proof(proj.id, 2, f"foto_cobertura_{time.time()}_gps_39.4153_-9.1345")

    print("\nA levantar disputa...")
    dispute = ledger.raise_dispute(proj.id,
                                   "Qualidade cobertura questionada - impermeabilizacao insuficiente")
    if dispute:
        votes = [VoteChoice.REJECT, VoteChoice.APPROVE, VoteChoice.APPROVE,
                 VoteChoice.APPROVE, VoteChoice.APPROVE]
        for member_id, choice in zip(dispute.council, votes):
            ledger.submit_vote(dispute.id, member_id, choice)
            time.sleep(0.1)

    print("\nA criar projecto de agricultura...")
    proj2 = ledger.create_project("maria", "Horta Comunitaria Sector B",
                                  "Expansao horta com rega gota-a-gota",
                                  ContributionType.AGRICULTURE)
    ledger.add_phase(proj2.id, "Preparacao terreno", 200.0)
    ledger.add_phase(proj2.id, "Sistema de rega",    350.0)
    ledger.submit_proof(proj2.id, 0, f"foto_terreno_{time.time()}")
    ledger.validate_phase(proj2.id, 0, "helena")
    ledger.pay_phase(proj2.id, 0)

    print("\nA aguardar mineracao...")
    time.sleep(6)
    blockchain.stop_mining()

    ledger.print_report()
    print("\nSIMULACAO CONCLUIDA")
    print("Pronto para migrar para Substrate quando o node estiver funcional.")


if __name__ == "__main__":
    run_simulation()
