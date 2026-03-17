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
        /// Evento disparado quando uma nova proposta é criada.
        /// [id_da_proposta]
        ProposalCreated { proposal_id: u32 },
    }

    // Estrutura base de erros para a palete de governança
    #[pallet::error]
    pub enum Error<T> {
        /// Exemplo: A proposta não foi encontrada
        ProposalNotFound,
        /// Exemplo: A votação para esta proposta já encerrou
        VotingClosed,
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        // As tuas funções (extrinsics) para criar propostas e votar entram aqui.
    }
}
