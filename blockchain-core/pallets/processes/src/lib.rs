#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::prelude::*;
    use frame_support::sp_runtime::traits::SaturatedConversion;

    use reputation::{ContributionType, Pallet as ReputationPallet};

    const MAX_PROCESS_DESCRIPTION: u32 = 1000;
    const MIN_REPUTATION_FOR_AUDIT: u32 = 1000;
    const MAX_AUDITS_PER_BLOCK: u32 = 10;

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProcessPhase {
        Creation,
        Execution,
        Audit,
        Resolution,
    }

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProcessStatus {
        Open,
        InAudit,
        Completed,
        Conflict,
        CompletedImmutable,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Process<T: Config> {
        id: u64,
        creator: T::AccountId,
        domain: ContributionType,
        description: BoundedVec<u8, ConstU32<MAX_PROCESS_DESCRIPTION>>,
        current_phase: ProcessPhase,
        status: ProcessStatus,
        buildcoin_value: u128,
        participants: BoundedVec<T::AccountId, T::MaxParticipants>,
        created_at: u32,
        updated_at: u32,
        audit_agent: Option<T::AccountId>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen, Default)]
    pub struct AuditAgentInfo {
        reputation_threshold: u32,
        domain_expertise: ContributionType,
        last_audit_block: u32,
        audit_count: u32,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen, Default)]
    pub enum AuditResult {
        #[default]
        Approved,
        Rejected,
        AnomalyDetected,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config + reputation::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        #[pallet::constant]
        type MaxParticipants: Get<u32> + Clone;

        type RootOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn next_process_id)]
    pub type NextProcessId<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn processes)]
    pub type Processes<T: Config> = StorageMap<_, Blake2_128Concat, u64, Process<T>, OptionQuery>;

    #[pallet::storage]
    #[pallet::getter(fn processes_by_domain)]
    pub type ProcessesByDomain<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, ContributionType,
        Blake2_128Concat, u64,
        (), ValueQuery
    >;

    #[pallet::storage]
    #[pallet::getter(fn qualified_audit_agents)]
    pub type QualifiedAuditAgents<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, AuditAgentInfo, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn audit_history)]
    pub type AuditHistory<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, T::AccountId,
        Blake2_128Concat, u64,
        AuditResult, ValueQuery
    >;

    #[pallet::storage]
    #[pallet::getter(fn immutable_processes)]
    pub type ImmutableProcesses<T: Config> = StorageMap<_, Blake2_128Concat, u64, Process<T>, OptionQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ProcessOpened(u64, T::AccountId, ContributionType),
        ProcessConcluded(u64, AuditResult),
        ProcessConflict(u64),
        BuildcoinsDistributed(u64, u128),
        AuditAgentRegistered(T::AccountId),
        AuditAgentDisqualified(T::AccountId),
    }

    #[pallet::error]
    pub enum Error<T> {
        ProcessNotFound,
        ProcessAlreadyCompleted,
        ProcessInWrongPhase,
        NotQualifiedAgent,
        InsufficientExpertise,
        ConflictOfInterest,
        MaxParticipantsReached,
        DescriptionTooLong,
        AgentAuditLimitReached,
        ProcessAlreadyInAudit,
        InvalidAuditResult,
        DistributionFailed,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {

        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn abrir_processo(
            origin: OriginFor<T>,
            domain: ContributionType,
            description: Vec<u8>,
            buildcoin_value: u128,
        ) -> DispatchResult {
            let creator = ensure_signed(origin)?;

            let bounded_description = BoundedVec::try_from(description)
                .map_err(|_| Error::<T>::DescriptionTooLong)?;

            let process_id = Self::next_process_id();
            NextProcessId::<T>::mutate(|id| *id += 1);

            let now: u32 = frame_system::Pallet::<T>::block_number().saturated_into();
            let process = Process {
                id: process_id,
                creator: creator.clone(),
                domain,
                description: bounded_description,
                current_phase: ProcessPhase::Creation,
                status: ProcessStatus::Open,
                buildcoin_value,
                participants: BoundedVec::new(),
                created_at: now,
                updated_at: now,
                audit_agent: None,
            };

            Processes::<T>::insert(process_id, process);
            ProcessesByDomain::<T>::insert(domain, process_id, ());

            Self::deposit_event(Event::ProcessOpened(process_id, creator, domain));
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn join_process(
            origin: OriginFor<T>,
            process_id: u64,
        ) -> DispatchResult {
            let participant = ensure_signed(origin)?;

            Processes::<T>::try_mutate(process_id, |maybe_process| {
                let process = maybe_process.as_mut().ok_or(Error::<T>::ProcessNotFound)?;

                ensure!(process.status == ProcessStatus::Open, Error::<T>::ProcessAlreadyCompleted);
                ensure!(
                    process.participants.len() < T::MaxParticipants::get() as usize,
                    Error::<T>::MaxParticipantsReached
                );
                ensure!(!process.participants.contains(&participant), Error::<T>::ConflictOfInterest);

                process.participants.try_push(participant)
                    .map_err(|_| Error::<T>::MaxParticipantsReached)?;

                process.updated_at = frame_system::Pallet::<T>::block_number().saturated_into();
                Ok(())
            })
        }

        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn concluir_processo(
            origin: OriginFor<T>,
            process_id: u64,
            audit_result: AuditResult,
        ) -> DispatchResultWithPostInfo {
            let audit_agent = ensure_signed(origin)?;

            ensure!(Self::is_qualified_audit_agent(&audit_agent), Error::<T>::NotQualifiedAgent);
            Self::execute_audit_logic(process_id, audit_agent, audit_result)?;

            Ok(().into())
        }

        #[pallet::call_index(3)]
        #[pallet::weight(10_000)]
        pub fn register_audit_agent(
            origin: OriginFor<T>,
            domain_expertise: ContributionType,
        ) -> DispatchResult {
            let agent = ensure_signed(origin)?;

            ensure!(
                Self::check_agent_qualification(&agent, domain_expertise),
                Error::<T>::InsufficientExpertise
            );

            let agent_info = AuditAgentInfo {
                reputation_threshold: MIN_REPUTATION_FOR_AUDIT,
                domain_expertise,
                last_audit_block: 0,
                audit_count: 0,
            };

            QualifiedAuditAgents::<T>::insert(&agent, agent_info);
            Self::deposit_event(Event::AuditAgentRegistered(agent));
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {

        fn is_qualified_audit_agent(agent: &T::AccountId) -> bool {
            let agent_info = Self::qualified_audit_agents(agent);
            agent_info.reputation_threshold > 0
        }

        fn check_agent_qualification(agent: &T::AccountId, domain: ContributionType) -> bool {
            let domain_reputation = ReputationPallet::<T>::get_reputation_by_type(agent.clone(), domain);
            if domain_reputation < MIN_REPUTATION_FOR_AUDIT {
                return false;
            }

            let current_block: u32 = frame_system::Pallet::<T>::block_number().saturated_into();
            let agent_info = Self::qualified_audit_agents(agent);

            if current_block.saturating_sub(agent_info.last_audit_block) < 100 {
                if agent_info.audit_count >= MAX_AUDITS_PER_BLOCK {
                    return false;
                }
            }

            true
        }

        fn agent_has_expertise(agent: &T::AccountId, domain: ContributionType) -> bool {
            let agent_info = Self::qualified_audit_agents(agent);
            agent_info.domain_expertise == domain
        }

        fn agent_is_involved(agent: &T::AccountId, process_id: u64) -> bool {
            if let Some(process) = Self::processes(process_id) {
                if process.creator == *agent {
                    return true;
                }
                if process.participants.contains(agent) {
                    return true;
                }
            }
            false
        }

        fn execute_audit_logic(
            process_id: u64,
            audit_agent: T::AccountId,
            audit_result: AuditResult,
        ) -> DispatchResult {
            let mut process = Self::processes(process_id).ok_or(Error::<T>::ProcessNotFound)?;

            ensure!(process.status != ProcessStatus::InAudit, Error::<T>::ProcessAlreadyInAudit);
            ensure!(process.status == ProcessStatus::Open, Error::<T>::ProcessInWrongPhase);
            ensure!(Self::is_qualified_audit_agent(&audit_agent), Error::<T>::NotQualifiedAgent);
            ensure!(Self::agent_has_expertise(&audit_agent, process.domain), Error::<T>::InsufficientExpertise);
            ensure!(!Self::agent_is_involved(&audit_agent, process_id), Error::<T>::ConflictOfInterest);

            let now: u32 = frame_system::Pallet::<T>::block_number().saturated_into();
            process.status = ProcessStatus::InAudit;
            process.audit_agent = Some(audit_agent.clone());
            process.updated_at = now;
            Processes::<T>::insert(process_id, process.clone());

            AuditHistory::<T>::insert(&audit_agent, process_id, audit_result.clone());

            match audit_result {
                AuditResult::Approved => {
                    Self::distribute_rewards(process_id)?;
                    process.status = ProcessStatus::Completed;
                }
                AuditResult::Rejected => {
                    process.status = ProcessStatus::Completed;
                }
                AuditResult::AnomalyDetected => {
                    Self::resolve_conflict(process_id)?;
                    process.status = ProcessStatus::Conflict;
                }
            }

            process.updated_at = frame_system::Pallet::<T>::block_number().saturated_into();
            Processes::<T>::insert(process_id, process);

            Self::make_process_immutable(process_id);
            Self::deposit_event(Event::ProcessConcluded(process_id, audit_result));
            Ok(())
        }

        fn distribute_rewards(process_id: u64) -> DispatchResult {
            let process = Self::processes(process_id).ok_or(Error::<T>::ProcessNotFound)?;

            let total_participants = process.participants.len() as u128;
            ensure!(total_participants > 0, Error::<T>::DistributionFailed);

            let reward_per_participant = process.buildcoin_value / total_participants;

            for participant in &process.participants {
                reputation::BuildcoinBalance::<T>::mutate(participant, |balance| {
                    *balance = balance.saturating_add(reward_per_participant);
                });
            }

            Self::deposit_event(Event::BuildcoinsDistributed(process_id, process.buildcoin_value));
            Ok(())
        }

        fn resolve_conflict(process_id: u64) -> DispatchResult {
            let process = Self::processes(process_id).ok_or(Error::<T>::ProcessNotFound)?;

            let top_experts = ReputationPallet::<T>::select_top_experts(process.domain);
            let council: Vec<T::AccountId> = top_experts
                .into_iter()
                .take(5)
                .map(|(account, _)| account)
                .collect();

            if council.len() >= 3 {
                Self::distribute_rewards(process_id)?;
            }

            Ok(())
        }

        fn make_process_immutable(process_id: u64) {
            if let Some(process) = Processes::<T>::take(process_id) {
                ImmutableProcesses::<T>::insert(process_id, process);
            }
        }
    }
}
