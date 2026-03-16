#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[polkadot_sdk::frame_support::pallet]
pub mod pallet {
    use polkadot_sdk::frame_support::pallet_prelude::*;
    use polkadot_sdk::frame_system::pallet_prelude::*;

    pub use reputation::pallet::{ContributionType, SubContributionType};

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
        Pending,
        InProgress,
        ProofSubmitted,
        Validated,
        Rejected,
        Paid,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Phase {
        pub index: u32,
        pub description: BoundedVec<u8, ConstU32<MAX_PHASE_DESC_LEN>>,
        pub proof_hash: Option<[u8; 32]>,
        pub status: PhaseStatus,
        pub payment_amount: u64,
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
    pub struct ProjectParticipant<AccountId: MaxEncodedLen> {
        pub project_id: u64,
        pub participant: AccountId,
        pub joined_at: u64,
        pub contribution_amount: u32,
        pub validated: bool,
    }

    #[pallet::config]
    pub trait Config: polkadot_sdk::frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as polkadot_sdk::frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type Projects<T: Config> = StorageMap<_, Blake2_128Concat, u64, Project<T::AccountId>, OptionQuery>;

    #[pallet::storage]
    pub type ProjectParticipants<T: Config> = StorageDoubleMap<_, Blake2_128Concat, u64, Blake2_128Concat, T::AccountId, ProjectParticipant<T::AccountId>, OptionQuery>;

    #[pallet::storage]
    pub type ProjectPhases<T: Config> = StorageDoubleMap<_, Blake2_128Concat, u64, Blake2_128Concat, u32, Phase, OptionQuery>;

    #[pallet::storage]
    pub type ProjectCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type ProjectsByStatus<T: Config> = StorageMap<_, Blake2_128Concat, ProjectStatus, BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>>, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    // CORREÇÃO: Removido o derive manual de Event, o SDK já faz isto automaticamente.
    pub enum Event<T: Config> {
        ProjectCreated(T::AccountId, u64, ContributionType),
        ProjectJoined(T::AccountId, u64),
        ProjectCompleted(T::AccountId, u64),
        ProjectEvaluated(u64, u32),
        ProjectCancelled(T::AccountId, u64),
    }

    #[pallet::error]
    pub enum Error<T> {
        ProjectNotFound,
        ProjectNotActive,
        NotParticipant,
        TooManyParticipants,
        TooManyProjects,
        Overflow,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::default())]
        pub fn create_project(
            origin: OriginFor<T>,
            name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
            description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
            domain: ContributionType,
            sub_domain: SubContributionType,
        ) -> DispatchResult {
            let creator = ensure_signed(origin)?;
            let project_id = ProjectCounter::<T>::get();
            
            let mut participants = BoundedVec::default();
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
                created_at: 0,
                completed_at: None,
                impact_score: None,
                total_phases: 0,
                phases_completed: 0,
            };

            Projects::<T>::insert(project_id, &project);
            ProjectCounter::<T>::put(project_id + 1);
            Self::deposit_event(Event::ProjectCreated(creator, project_id, domain));
            Ok(())
        }
    }
}
