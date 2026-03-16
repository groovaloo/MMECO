#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[polkadot_sdk::frame_support::pallet]
pub mod pallet {
    use polkadot_sdk::frame_support::pallet_prelude::*;
    use polkadot_sdk::frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: polkadot_sdk::frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as polkadot_sdk::frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    // ESTA É A ALTERAÇÃO: Adicionámos o Encode, Decode e TypeInfo
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub enum Event<T: Config> {
        ReputationUpdated(T::AccountId, u32),
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::default())]
        pub fn update_reputation(origin: OriginFor<T>, target: T::AccountId, score: u32) -> DispatchResult {
            ensure_root(origin)?; 
            Self::deposit_event(Event::ReputationUpdated(target, score));
            Ok(())
        }
    }

    // Função necessária para a compatibilidade entre as pallets
    impl<T: Config> Pallet<T> {
        pub fn select_top_experts(_domain: polkadot_sdk::sp_std::vec::Vec<u8>) -> polkadot_sdk::sp_std::vec::Vec<(T::AccountId, u32)> {
            polkadot_sdk::sp_std::vec::Vec::new()
        }
    }
}
