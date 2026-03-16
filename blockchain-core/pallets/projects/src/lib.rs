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
    // CORREÇÃO CRÍTICA: Adicionado Encode, Decode e TypeInfo para o SDK 2025
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub enum Event<T: Config> {
        ProjectCreated(T::AccountId, u32),
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::default())]
        pub fn create_project(origin: OriginFor<T>, id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Lógica simples de emissão de evento
            Self::deposit_event(Event::ProjectCreated(who, id));
            Ok(())
        }
    }
}
