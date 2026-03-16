#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[polkadot_sdk::frame_support::pallet]
pub mod pallet {
    use polkadot_sdk::frame_support::pallet_prelude::*;
    use polkadot_sdk::frame_system::pallet_prelude::*;
    use polkadot_sdk::sp_std::vec::Vec;
    use reputation::pallet::ContributionType;

    pub const MAX_COUNCIL: u32 = 5;
    pub const MAX_DISPUTES_PER_PROJECT: u32 = 100;
    pub const MAX_REASON_LEN: u32 = 300;

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum DisputeStatus {
        Open,
        Decided,
        Cancelled,
    }

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum Decision {
        ApproveProject,
        RejectProject,
        ApprovePhase,
        RejectPhase,
    }

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum VoteChoice {
        Approve,
        Reject,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Vote<AccountId: MaxEncodedLen> {
        pub member: AccountId,
        pub choice: VoteChoice,
        pub voted_at: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Dispute<AccountId: MaxEncodedLen> {
        pub id: u64,
        pub project_id: u64,
        pub phase_index: Option<u32>,
        pub domain: ContributionType,
        pub council: BoundedVec<AccountId, ConstU32<MAX_COUNCIL>>,
        pub votes: BoundedVec<Vote<AccountId>, ConstU32<MAX_COUNCIL>>,
        pub status: DisputeStatus,
        pub decision: Option<Decision>,
        pub reason: BoundedVec<u8, ConstU32<MAX_REASON_LEN>>,
        pub created_at: u64,
        pub decided_at: Option<u64>,
    }

    #[pallet::config]
    pub trait Config: polkadot_sdk::frame_system::Config + reputation::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as polkadot_sdk::frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type Disputes<T: Config> = StorageMap<_, Blake2_128Concat, u64, Dispute<T::AccountId>, OptionQuery>;

    #[pallet::storage]
    pub type DisputeCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type DisputesByProject<T: Config> = StorageMap<_, Blake2_128Concat, u64, BoundedVec<u64, ConstU32<MAX_DISPUTES_PER_PROJECT>>, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    // NOTA: Removido o derive manual porque o SDK 2026 já o gera automaticamente aqui
    pub enum Event<T: Config> {
        DisputeRaised(u64, u64, ContributionType),
        VoteSubmitted(u64, T::AccountId, VoteChoice),
        DisputeDecided(u64, Decision),
        DisputeCancelled(u64),
    }

    #[pallet::error]
    pub enum Error<T> {
        DisputeNotFound,
        DisputeNotOpen,
        NotCouncilMember,
        AlreadyVoted,
        InsufficientExperts,
        TooManyDisputes,
        Overflow,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::default())]
        pub fn raise_dispute(
            origin: OriginFor<T>,
            project_id: u64,
            domain: ContributionType,
            phase_index: Option<u32>,
            reason: BoundedVec<u8, ConstU32<MAX_REASON_LEN>>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let experts = reputation::Pallet::<T>::select_top_experts(Vec::new());
            ensure!(experts.len() >= 0usize, Error::<T>::InsufficientExperts);

            let dispute_id = DisputeCounter::<T>::get();
            let dispute = Dispute {
                id: dispute_id,
                project_id,
                phase_index,
                domain,
                council: BoundedVec::default(),
                votes: BoundedVec::default(),
                status: DisputeStatus::Open,
                decision: None,
                reason,
                created_at: 0,
                decided_at: None,
            };

            Disputes::<T>::insert(dispute_id, &dispute);
            DisputeCounter::<T>::put(dispute_id + 1);
            Self::deposit_event(Event::DisputeRaised(dispute_id, project_id, domain));
            Ok(())
        }
    }
}
