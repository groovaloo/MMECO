#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::prelude::*;

    const MAX_REPUTATION: u32 = 1_000_000;

    #[derive(
        Encode,
        Decode,
        Clone,
        Copy,
        PartialEq,
        Eq,
        RuntimeDebug,
        TypeInfo,
        MaxEncodedLen
    )]
    pub enum ContributionType {
        Construction,
        Agriculture,
        Energy,
        Governance,
        Health,
        Logistics,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>>
            + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // Admin do Sistema
    #[pallet::storage]
    #[pallet::getter(fn admin)]
    pub type Admin<T: Config> = StorageValue<_, T::AccountId>;

    // Reputação Total
    #[pallet::storage]
    #[pallet::getter(fn reputation)]
    pub type Reputation<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    // Reputação por Tipo (Domínio)
    #[pallet::storage]
    #[pallet::getter(fn reputation_by_type)]
    pub type ReputationByType<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, T::AccountId,
        Blake2_128Concat, ContributionType,
        u32,
        ValueQuery
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ContributionRecorded(T::AccountId, ContributionType, u32),
        ReputationReduced(T::AccountId, ContributionType, u32),
        ReputationReset(T::AccountId),
        AdminSet(T::AccountId),
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
        #[pallet::weight(10_000)]
        pub fn set_admin(origin: OriginFor<T>, new_admin: T::AccountId) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            Admin::<T>::put(&new_admin);
            Self::deposit_event(Event::AdminSet(new_admin));
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
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

            Reputation::<T>::try_mutate(&who, |rep| -> Result<(), Error<T>> {
                let new_rep = rep.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                if new_rep > MAX_REPUTATION {
                    return Err(Error::<T>::MaxReputationReached)
                }
                *rep = new_rep;
                Ok(())
            })?;

            Self::deposit_event(Event::ContributionRecorded(who, contribution, amount));
            Ok(())
        }

        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn reduce_contribution(
            origin: OriginFor<T>,
            contribution: ContributionType,
            amount: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ReputationByType::<T>::try_mutate(&who, contribution, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_sub(amount).ok_or(Error::<T>::Underflow)?;
                Ok(())
            })?;

            Reputation::<T>::try_mutate(&who, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_sub(amount).ok_or(Error::<T>::Underflow)?;
                Ok(())
            })?;

            Self::deposit_event(Event::ReputationReduced(who, contribution, amount));
            Ok(())
        }

        #[pallet::call_index(3)]
        #[pallet::weight(10_000)]
        pub fn reset_reputation(origin: OriginFor<T>, target: T::AccountId) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let admin = Admin::<T>::get().ok_or(Error::<T>::NotAdmin)?;
            ensure!(who == admin, Error::<T>::NotAdmin);

            Reputation::<T>::insert(&target, 0);

            // Loop de limpeza atualizado para os 6 domínios
            for t in [
                ContributionType::Construction,
                ContributionType::Agriculture,
                ContributionType::Energy,
                ContributionType::Governance,
                ContributionType::Health,
                ContributionType::Logistics,
            ] {
                ReputationByType::<T>::insert(&target, t, 0);
            }

            Self::deposit_event(Event::ReputationReset(target));
            Ok(())
        }
    }

    // Funções de Consulta (Leitura)
    impl<T: Config> Pallet<T> {
        pub fn get_reputation(account: T::AccountId) -> u32 {
            Reputation::<T>::get(account)
        }

        pub fn get_reputation_by_type(account: T::AccountId, contribution: ContributionType) -> u32 {
            ReputationByType::<T>::get(account, contribution)
        }
    }
}