#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[polkadot_sdk::frame_support::pallet]
pub mod pallet {
    use polkadot_sdk::frame_support::pallet_prelude::*;
    use polkadot_sdk::frame_system::pallet_prelude::*;
    use polkadot_sdk::sp_std::vec::Vec;

    const MAX_REPUTATION: u32 = 1_000_000;

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ContributionType {
        Construction,
        Agriculture,
        Energy,
        Governance,
        Health,
        Logistics,
    }

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum SubContributionType {
        Painting, Carpentry, Masonry, Electrical, Plumbing,
        CropFarming, Livestock, Horticulture,
        Solar, Wind, Hydro,
        Medical, Nursing, FirstAid,
        Transport, Storage, Distribution,
        Coordination, Mediation, Planning,
    }

    #[pallet::config]
    pub trait Config: polkadot_sdk::frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as polkadot_sdk::frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type Admin<T: Config> = StorageValue<_, T::AccountId>;

    #[pallet::storage]
    pub type Reputation<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    #[pallet::storage]
    pub type ReputationByType<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, T::AccountId,
        Blake2_128Concat, ContributionType,
        u32,
        ValueQuery
    >;

    #[pallet::storage]
    pub type BuildcoinBalance<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u128, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    // CORREÇÃO: Removido o derive manual. O SDK 2026 trata disto automaticamente.
    pub enum Event<T: Config> {
        ContributionRecorded(T::AccountId, ContributionType, u32),
        ReputationReduced(T::AccountId, ContributionType, u32),
        ReputationReset(T::AccountId),
        AdminSet(T::AccountId),
        BuildcoinMinted(T::AccountId, u128),
    }

    #[pallet::error]
    pub enum Error<T> {
        Overflow,
        Underflow,
        MaxReputationReached,
        NotAdmin,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::default())]
        pub fn set_admin(origin: OriginFor<T>, new_admin: T::AccountId) -> DispatchResult {
            ensure_root(origin)?; 
            Admin::<T>::put(&new_admin);
            Self::deposit_event(Event::AdminSet(new_admin));
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(Weight::default())]
        pub fn record_contribution(
            origin: OriginFor<T>,
            contribution: ContributionType,
            amount: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ReputationByType::<T>::try_mutate(&who, contribution, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                Ok(())
            })?;
            Self::deposit_event(Event::ContributionRecorded(who, contribution, amount));
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn select_top_experts(contribution_type: Vec<u8>) -> Vec<(T::AccountId, u32)> {
            Vec::new() // Placeholder simplificado para compilação
        }
    }
}
