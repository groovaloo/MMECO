#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// O tipo de evento que a blockchain vai emitir.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Evento disparado quando a reputação de uma conta é atualizada.
        /// [account_id, nova_reputacao]
        ReputationUpdated { who: T::AccountId, amount: u32 },
    }

    // Estrutura base de erros (sempre útil ter preparada para o Polkadot moderno)
    #[pallet::error]
    pub enum Error<T> {
        /// Exemplo de erro: Reputação não pode ser negativa
        ReputationTooLow,
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        // As tuas funções de transação (extrinsics) vão entrar aqui no futuro.
        // O Polkadot SDK moderno exige que fiquem bem isoladas aqui dentro.
    }
}
