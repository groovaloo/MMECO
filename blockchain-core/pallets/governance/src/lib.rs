#![cfg_attr(not(feature = "std"), no_std)]

// pallet exported via macro

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::prelude::*;
    use pallet_reputation::pallet::ContributionType;

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
    pub trait Config: frame_system::Config + pallet_reputation::Config<AccountId = <Self as frame_system::Config>::AccountId> {
        type RuntimeEvent: From<Event<Self>>
            + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn dispute)]
    pub type Disputes<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64,
        Dispute<<T as frame_system::Config>::AccountId>,
        OptionQuery
    >;

    #[pallet::storage]
    #[pallet::getter(fn dispute_counter)]
    pub type DisputeCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn disputes_by_project)]
    pub type DisputesByProject<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64,
        BoundedVec<u64, ConstU32<MAX_DISPUTES_PER_PROJECT>>,
        ValueQuery
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        DisputeRaised(u64, u64, ContributionType),
        VoteSubmitted(u64, <T as frame_system::Config>::AccountId, VoteChoice),
        DisputeDecided(u64, Decision),
        DisputeCancelled(u64),
    }

    #[pallet::error]
    pub enum Error<T> {
        ProjectNotFound,
        ProjectNotActive,
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
        #[pallet::weight(10_000)]
        pub fn raise_dispute(
            origin: OriginFor<T>,
            project_id: u64,
            domain: ContributionType,
            phase_index: Option<u32>,
            reason: BoundedVec<u8, ConstU32<MAX_REASON_LEN>>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let experts = pallet_reputation::Pallet::<T>::select_top_experts(domain);
            ensure!(experts.len() >= 3usize, Error::<T>::InsufficientExperts);

            let block = <frame_system::Pallet<T>>::block_number();
            let created_at: u64 = block.try_into().unwrap_or(0u64);

            let dispute_id = Self::dispute_counter();

            let mut council: BoundedVec<
                <T as frame_system::Config>::AccountId,
                ConstU32<MAX_COUNCIL>
            > = BoundedVec::default();

            for (account, _rep) in experts.into_iter() {
                let _ = council.try_push(account);
            }

            let dispute = Dispute {
                id: dispute_id,
                project_id,
                phase_index,
                domain,
                council,
                votes: BoundedVec::default(),
                status: DisputeStatus::Open,
                decision: None,
                reason,
                created_at,
                decided_at: None,
            };

            Disputes::<T>::insert(dispute_id, &dispute);
            DisputeCounter::<T>::set(dispute_id + 1);

            DisputesByProject::<T>::try_mutate(project_id, |v| {
                v.try_push(dispute_id)
            }).map_err(|_| Error::<T>::TooManyDisputes)?;

            Self::deposit_event(Event::DisputeRaised(dispute_id, project_id, domain));
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn submit_vote(
            origin: OriginFor<T>,
            dispute_id: u64,
            choice: VoteChoice,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut dispute = Self::dispute(dispute_id)
                .ok_or(Error::<T>::DisputeNotFound)?;

            ensure!(dispute.status == DisputeStatus::Open, Error::<T>::DisputeNotOpen);

            ensure!(
                dispute.council.iter().any(|m| m == &who),
                Error::<T>::NotCouncilMember
            );

            ensure!(
                !dispute.votes.iter().any(|v| v.member == who),
                Error::<T>::AlreadyVoted
            );

            let block = <frame_system::Pallet<T>>::block_number();
            let voted_at: u64 = block.try_into().unwrap_or(0u64);

            let vote = Vote {
                member: who.clone(),
                choice,
                voted_at,
            };

            dispute.votes.try_push(vote).map_err(|_| Error::<T>::Overflow)?;

            Self::deposit_event(Event::VoteSubmitted(dispute_id, who, choice));

            let approve_votes = dispute.votes.iter()
                .filter(|v| v.choice == VoteChoice::Approve)
                .count();
            let reject_votes = dispute.votes.iter()
                .filter(|v| v.choice == VoteChoice::Reject)
                .count();
            let majority = (dispute.council.len() / 2) + 1;

            if approve_votes >= majority {
                dispute.status = DisputeStatus::Decided;
                dispute.decision = Some(Decision::ApproveProject);
                dispute.decided_at = Some(voted_at);
                Disputes::<T>::insert(dispute_id, &dispute);
                Self::deposit_event(Event::DisputeDecided(dispute_id, Decision::ApproveProject));
            } else if reject_votes >= majority {
                dispute.status = DisputeStatus::Decided;
                dispute.decision = Some(Decision::RejectProject);
                dispute.decided_at = Some(voted_at);
                Disputes::<T>::insert(dispute_id, &dispute);
                Self::deposit_event(Event::DisputeDecided(dispute_id, Decision::RejectProject));
            } else {
                Disputes::<T>::insert(dispute_id, &dispute);
            }

            Ok(())
        }

        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn cancel_dispute(
            origin: OriginFor<T>,
            dispute_id: u64,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut dispute = Self::dispute(dispute_id)
                .ok_or(Error::<T>::DisputeNotFound)?;

            ensure!(dispute.status == DisputeStatus::Open, Error::<T>::DisputeNotOpen);

            dispute.status = DisputeStatus::Cancelled;
            Disputes::<T>::insert(dispute_id, &dispute);

            Self::deposit_event(Event::DisputeCancelled(dispute_id));
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn get_dispute(
            dispute_id: u64,
        ) -> Option<Dispute<<T as frame_system::Config>::AccountId>> {
            Self::dispute(dispute_id)
        }

        pub fn get_disputes_by_project(
            project_id: u64,
        ) -> BoundedVec<u64, ConstU32<MAX_DISPUTES_PER_PROJECT>> {
            Self::disputes_by_project(project_id)
        }
    }
}
