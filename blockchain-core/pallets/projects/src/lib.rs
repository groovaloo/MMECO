#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    pub use pallet_reputation::pallet::{ContributionType, SubContributionType};

    pub const MAX_NAME_LEN: u32 = 100;
    pub const MAX_DESC_LEN: u32 = 500;
    pub const MAX_PARTICIPANTS: u32 = 256;
    pub const MAX_PROJECTS_PER_STATUS: u32 = 10_000;
    pub const MAX_PHASES: u32 = 100;
    pub const MAX_PHASE_DESC_LEN: u32 = 200;

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProjectStatus {
        Created,
        Active,
        Completed,
        Evaluated,
        Cancelled,
    }

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum PhaseStatus {
        Pending,       // Fase definida, ainda não iniciada
        InProgress,    // Fase em execução
        ProofSubmitted, // Prova submetida, aguarda validação IA
        Validated,     // Validada pelo agente IA
        Rejected,      // Rejeitada pelo agente IA
        Paid,          // Pagamento efectuado
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Phase {
        pub index: u32,
        pub description: BoundedVec<u8, ConstU32<MAX_PHASE_DESC_LEN>>,
        pub proof_hash: Option<[u8; 32]>,   // SHA-256 da foto
        pub status: PhaseStatus,
        pub payment_amount: u64,            // Buildcoin a pagar nesta fase
        pub submitted_at: Option<u64>,
        pub validated_at: Option<u64>,
        pub paid_at: Option<u64>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Project<AccountId: MaxEncodedLen> {
        pub id: u64,
        pub creator: AccountId,
        pub name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
        pub description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
        pub domain: ContributionType,
        pub sub_domain: SubContributionType,
        pub status: ProjectStatus,
        pub participants: BoundedVec<AccountId, ConstU32<MAX_PARTICIPANTS>>,
        pub created_at: u64,
        pub completed_at: Option<u64>,
        pub impact_score: Option<u32>,
        pub total_phases: u32,
        pub phases_completed: u32,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct ProjectParticipant<AccountId> {
        pub project_id: u64,
        pub participant: AccountId,
        pub joined_at: u64,
        pub contribution_amount: u32,
        pub validated: bool,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>>
            + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Reputation: frame_system::Config + pallet_reputation::Config;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn project)]
    pub type Projects<T: Config> = StorageMap<
        _, Blake2_128Concat, u64, Project<T::AccountId>, OptionQuery
    >;

    #[pallet::storage]
    #[pallet::getter(fn project_participant)]
    pub type ProjectParticipants<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, u64,
        Blake2_128Concat, T::AccountId,
        ProjectParticipant<T::AccountId>,
        OptionQuery
    >;

    // Fases dinâmicas: project_id -> phase_index -> Phase
    #[pallet::storage]
    #[pallet::getter(fn project_phase)]
    pub type ProjectPhases<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, u64,
        Blake2_128Concat, u32,
        Phase,
        OptionQuery
    >;

    #[pallet::storage]
    #[pallet::getter(fn project_counter)]
    pub type ProjectCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn projects_by_status)]
    pub type ProjectsByStatus<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ProjectStatus,
        BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>>,
        ValueQuery
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ProjectCreated(T::AccountId, u64, ContributionType),
        ProjectJoined(T::AccountId, u64),
        ProjectCompleted(T::AccountId, u64),
        ProjectEvaluated(u64, u32),
        ProjectCancelled(T::AccountId, u64),
        PhaseAdded(u64, u32, u64),            // project_id, phase_index, payment_amount
        ProofSubmitted(u64, u32, [u8; 32]),   // project_id, phase_index, proof_hash
        PhaseValidated(u64, u32),             // project_id, phase_index
        PhaseRejected(u64, u32),              // project_id, phase_index
        PhasePaid(u64, u32, u64),             // project_id, phase_index, amount
    }

    #[pallet::error]
    pub enum Error<T> {
        ProjectNotFound,
        ProjectAlreadyCompleted,
        ProjectNotActive,
        ProjectNotCompleted,
        AlreadyParticipant,
        NotParticipant,
        NotProjectCreator,
        MaxProjectNameLengthExceeded,
        MaxProjectDescriptionLengthExceeded,
        InvalidImpactScore,
        Overflow,
        TooManyParticipants,
        TooManyProjects,
        PhaseNotFound,
        PhaseNotInProgress,
        PhaseNotSubmitted,
        PhaseAlreadyValidated,
        TooManyPhases,
        InvalidPhaseIndex,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {

        /// Criar projecto
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn create_project(
            origin: OriginFor<T>,
            name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
            description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
            domain: ContributionType,
            sub_domain: SubContributionType,
        ) -> DispatchResult {
            let creator = ensure_signed(origin)?;

            let project_id = Self::project_counter();
            let block = <frame_system::Pallet<T>>::block_number();
            let created_at: u64 = block.try_into().unwrap_or(0u64);

            let mut participants: BoundedVec<T::AccountId, ConstU32<MAX_PARTICIPANTS>> =
                BoundedVec::default();
            participants.try_push(creator.clone()).map_err(|_| Error::<T>::TooManyParticipants)?;

            let project = Project {
                id: project_id,
                creator: creator.clone(),
                name,
                description,
                domain,
                sub_domain,
                status: ProjectStatus::Created,
                participants,
                created_at,
                completed_at: None,
                impact_score: None,
                total_phases: 0,
                phases_completed: 0,
            };

            Projects::<T>::insert(project_id, &project);

            let participant = ProjectParticipant {
                project_id,
                participant: creator.clone(),
                joined_at: created_at,
                contribution_amount: 0,
                validated: false,
            };
            ProjectParticipants::<T>::insert(project_id, &creator, participant);
            ProjectCounter::<T>::set(project_id + 1);

            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Created, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCreated(creator, project_id, domain));
            Ok(())
        }

        /// Agente IA adiciona uma fase ao projecto
        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn add_phase(
            origin: OriginFor<T>,
            project_id: u64,
            description: BoundedVec<u8, ConstU32<MAX_PHASE_DESC_LEN>>,
            payment_amount: u64,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(
                project.status == ProjectStatus::Created || project.status == ProjectStatus::Active,
                Error::<T>::ProjectNotActive
            );
            ensure!(project.total_phases < MAX_PHASES, Error::<T>::TooManyPhases);

            let phase_index = project.total_phases;

            let phase = Phase {
                index: phase_index,
                description,
                proof_hash: None,
                status: PhaseStatus::Pending,
                payment_amount,
                submitted_at: None,
                validated_at: None,
                paid_at: None,
            };

            ProjectPhases::<T>::insert(project_id, phase_index, &phase);

            project.total_phases = project.total_phases
                .checked_add(1)
                .ok_or(Error::<T>::Overflow)?;
            Projects::<T>::insert(project_id, &project);

            Self::deposit_event(Event::PhaseAdded(project_id, phase_index, payment_amount));
            Ok(())
        }

        /// Participante submete prova (hash SHA-256 da foto)
        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn submit_proof(
            origin: OriginFor<T>,
            project_id: u64,
            phase_index: u32,
            proof_hash: [u8; 32],
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                Self::project_participant(project_id, &who).is_some(),
                Error::<T>::NotParticipant
            );

            let mut phase = Self::project_phase(project_id, phase_index)
                .ok_or(Error::<T>::PhaseNotFound)?;

            ensure!(
                phase.status == PhaseStatus::Pending || phase.status == PhaseStatus::InProgress,
                Error::<T>::PhaseNotInProgress
            );

            let block = <frame_system::Pallet<T>>::block_number();
            let submitted_at: u64 = block.try_into().unwrap_or(0u64);

            phase.proof_hash = Some(proof_hash);
            phase.status = PhaseStatus::ProofSubmitted;
            phase.submitted_at = Some(submitted_at);

            ProjectPhases::<T>::insert(project_id, phase_index, &phase);

            Self::deposit_event(Event::ProofSubmitted(project_id, phase_index, proof_hash));
            Ok(())
        }

        /// Agente IA valida a fase
        #[pallet::call_index(3)]
        #[pallet::weight(10_000)]
        pub fn validate_phase(
            origin: OriginFor<T>,
            project_id: u64,
            phase_index: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut phase = Self::project_phase(project_id, phase_index)
                .ok_or(Error::<T>::PhaseNotFound)?;

            ensure!(phase.status == PhaseStatus::ProofSubmitted, Error::<T>::PhaseNotSubmitted);

            let block = <frame_system::Pallet<T>>::block_number();
            let validated_at: u64 = block.try_into().unwrap_or(0u64);

            phase.status = PhaseStatus::Validated;
            phase.validated_at = Some(validated_at);
            ProjectPhases::<T>::insert(project_id, phase_index, &phase);

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            project.phases_completed = project.phases_completed
                .checked_add(1)
                .ok_or(Error::<T>::Overflow)?;
            Projects::<T>::insert(project_id, &project);

            Self::deposit_event(Event::PhaseValidated(project_id, phase_index));
            Ok(())
        }

        /// Agente IA rejeita a fase
        #[pallet::call_index(4)]
        #[pallet::weight(10_000)]
        pub fn reject_phase(
            origin: OriginFor<T>,
            project_id: u64,
            phase_index: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut phase = Self::project_phase(project_id, phase_index)
                .ok_or(Error::<T>::PhaseNotFound)?;

            ensure!(phase.status == PhaseStatus::ProofSubmitted, Error::<T>::PhaseNotSubmitted);

            phase.status = PhaseStatus::Rejected;
            ProjectPhases::<T>::insert(project_id, phase_index, &phase);

            Self::deposit_event(Event::PhaseRejected(project_id, phase_index));
            Ok(())
        }

        /// Regista pagamento de fase validada
        #[pallet::call_index(5)]
        #[pallet::weight(10_000)]
        pub fn pay_phase(
            origin: OriginFor<T>,
            project_id: u64,
            phase_index: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut phase = Self::project_phase(project_id, phase_index)
                .ok_or(Error::<T>::PhaseNotFound)?;

            ensure!(phase.status == PhaseStatus::Validated, Error::<T>::PhaseAlreadyValidated);

            let block = <frame_system::Pallet<T>>::block_number();
            let paid_at: u64 = block.try_into().unwrap_or(0u64);

            let amount = phase.payment_amount;
            phase.status = PhaseStatus::Paid;
            phase.paid_at = Some(paid_at);
            ProjectPhases::<T>::insert(project_id, phase_index, &phase);

            Self::deposit_event(Event::PhasePaid(project_id, phase_index, amount));
            Ok(())
        }

        /// Entrar no projecto
        #[pallet::call_index(6)]
        #[pallet::weight(10_000)]
        pub fn join_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let participant = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(
                project.status == ProjectStatus::Created || project.status == ProjectStatus::Active,
                Error::<T>::ProjectNotActive
            );
            ensure!(
                Self::project_participant(project_id, &participant).is_none(),
                Error::<T>::AlreadyParticipant
            );

            let block = <frame_system::Pallet<T>>::block_number();
            let joined_at: u64 = block.try_into().unwrap_or(0u64);

            let participant_record = ProjectParticipant {
                project_id,
                participant: participant.clone(),
                joined_at,
                contribution_amount: 0,
                validated: false,
            };
            ProjectParticipants::<T>::insert(project_id, &participant, participant_record);

            if project.status == ProjectStatus::Created {
                project.status = ProjectStatus::Active;
                Projects::<T>::insert(project_id, &project);
                ProjectsByStatus::<T>::mutate(ProjectStatus::Created, |v| {
                    v.retain(|&id| id != project_id);
                });
                ProjectsByStatus::<T>::try_mutate(ProjectStatus::Active, |v| {
                    v.try_push(project_id)
                }).map_err(|_| Error::<T>::TooManyProjects)?;
            }

            Self::deposit_event(Event::ProjectJoined(participant, project_id));
            Ok(())
        }

        /// Concluir projecto
        #[pallet::call_index(7)]
        #[pallet::weight(10_000)]
        pub fn complete_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.creator == who, Error::<T>::NotProjectCreator);
            ensure!(project.status == ProjectStatus::Active, Error::<T>::ProjectNotActive);

            let block = <frame_system::Pallet<T>>::block_number();
            let completed_at: u64 = block.try_into().unwrap_or(0u64);

            project.status = ProjectStatus::Completed;
            project.completed_at = Some(completed_at);
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Active, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Completed, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCompleted(who, project_id));
            Ok(())
        }

        /// Avaliar projecto concluído
        #[pallet::call_index(8)]
        #[pallet::weight(10_000)]
        pub fn evaluate_project(
            origin: OriginFor<T>,
            project_id: u64,
            impact_score: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.status == ProjectStatus::Completed, Error::<T>::ProjectNotCompleted);
            ensure!(impact_score > 0 && impact_score <= 1000, Error::<T>::InvalidImpactScore);

            project.status = ProjectStatus::Evaluated;
            project.impact_score = Some(impact_score);
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Completed, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Evaluated, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectEvaluated(project_id, impact_score));
            Ok(())
        }

        /// Cancelar projecto
        #[pallet::call_index(9)]
        #[pallet::weight(10_000)]
        pub fn cancel_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.creator == who, Error::<T>::NotProjectCreator);
            ensure!(
                project.status == ProjectStatus::Created || project.status == ProjectStatus::Active,
                Error::<T>::ProjectNotActive
            );

            project.status = ProjectStatus::Cancelled;
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Created, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::mutate(ProjectStatus::Active, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Cancelled, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCancelled(who, project_id));
            Ok(())
        }

        /// Registar contribuição
        #[pallet::call_index(10)]
        #[pallet::weight(10_000)]
        pub fn record_contribution(
            origin: OriginFor<T>,
            project_id: u64,
            contribution_amount: u32,
        ) -> DispatchResult {
            let participant = ensure_signed(origin)?;

            let project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.status == ProjectStatus::Active, Error::<T>::ProjectNotActive);

            let mut participant_record = Self::project_participant(project_id, &participant)
                .ok_or(Error::<T>::NotParticipant)?;

            participant_record.contribution_amount = participant_record.contribution_amount
                .checked_add(contribution_amount)
                .ok_or(Error::<T>::Overflow)?;

            ProjectParticipants::<T>::insert(project_id, &participant, participant_record);
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn get_projects_by_status(status: ProjectStatus) -> BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>> {
            Self::projects_by_status(status)
        }

        pub fn get_project(project_id: u64) -> Option<Project<T::AccountId>> {
            Self::project(project_id)
        }

        pub fn get_phase(project_id: u64, phase_index: u32) -> Option<Phase> {
            Self::project_phase(project_id, phase_index)
        }

        pub fn get_project_participants(project_id: u64) -> sp_std::vec::Vec<T::AccountId> {
            let mut participants = sp_std::vec::Vec::new();
            for (pid, participant, _) in ProjectParticipants::<T>::iter() {
                if pid == project_id {
                    participants.push(participant);
                }
            }
            participants
        }
    }
}
