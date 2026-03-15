#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::{
    derive_impl, parameter_types, traits::Everything,
};
use polkadot_sdk::sp_runtime::{
    generic, traits::{BlakeTwo256, IdentityLookup},
    MultiSignature, MultiAddress,
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};
use polkadot_sdk::frame_system;

// Pallets da Moral Money
pub use reputation;
pub use pallet_projects;
pub use pallet_governance;

pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;

// CORREÇÃO CRÍTICA: Uso de caminhos absolutos do sp_runtime para evitar erro de Encode/Decode
pub type UncheckedExtrinsic = polkadot_sdk::sp_runtime::generic::UncheckedExtrinsic<
    polkadot_sdk::sp_core::sr25519::Public,
    RuntimeCall,
    MultiSignature,
    SignedExtra,
>;

// Definimos o SignedExtra padrão para o Polkadot SDK 2025
pub type SignedExtra = (
    polkadot_sdk::frame_system::CheckNonZeroSender<Runtime>,
    polkadot_sdk::frame_system::CheckSpecVersion<Runtime>,
    polkadot_sdk::frame_system::CheckTxVersion<Runtime>,
    polkadot_sdk::frame_system::CheckGenesis<Runtime>,
    polkadot_sdk::frame_system::CheckEra<Runtime>,
    polkadot_sdk::frame_system::CheckNonce<Runtime>,
    polkadot_sdk::frame_system::CheckWeight<Runtime>,
    polkadot_sdk::pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);

pub type Block = polkadot_sdk::sp_runtime::generic::Block<Header, UncheckedExtrinsic>;

parameter_types! {
    pub const BlockHashCount: BlockNumber = 250;
    pub const SS58Prefix: u8 = 42;
    pub const Version: RuntimeVersion = RuntimeVersion {
        spec_name: polkadot_sdk::sp_version::create_runtime_str!("moral-money"),
        impl_name: polkadot_sdk::sp_version::create_runtime_str!("moral-money"),
        authoring_version: 1,
        spec_version: 1,
        impl_version: 1,
        apis: polkadot_sdk::sp_version::create_apis_vec!([]),
        transaction_version: 1,
        state_version: 1,
    };
}

// Implementação com derive_impl para simplificar as centenas de erros anteriores
#[derive_impl(polkadot_sdk::frame_system::config_preludes::SolochainDefaultConfig)]
impl frame_system::Config for Runtime {
    type Block = Block;
    type AccountId = polkadot_sdk::sp_core::sr25519::Public;
    type Lookup = IdentityLookup<Self::AccountId>;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type RuntimeOrigin = RuntimeOrigin;
    type Version = Version;
    type SS58Prefix = SS58Prefix;
    type MaxConsumers = polkadot_sdk::frame_support::traits::ConstU32<16>;
    type AccountData = (); // Ajustado para coincidir com o teu código original
}

impl reputation::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}

impl pallet_governance::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}

impl pallet_projects::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Reputation = Runtime;
}

// Macro de Runtime moderna (Obrigatória no SDK 2025)
#[polkadot_sdk::frame_support::runtime]
mod runtime {
    #[runtime::runtime]
    #[runtime::derive(
        RuntimeCall,
        RuntimeEvent,
        RuntimeError,
        RuntimeOrigin,
        RuntimeFreezeReason,
        RuntimeHoldReason,
        RuntimeSlashReason,
        RuntimeLockId,
        RuntimeTask
    )]
    pub struct Runtime;

    #[runtime::pallet_index(0)]
    pub type System = polkadot_sdk::frame_system::Pallet<Runtime>;

    #[runtime::pallet_index(1)]
    pub type Reputation = reputation::Pallet<Runtime>;

    #[runtime::pallet_index(2)]
    pub type Projects = pallet_projects::Pallet<Runtime>;

    #[runtime::pallet_index(3)]
    pub type Governance = pallet_governance::Pallet<Runtime>;
}

pub type Executive = polkadot_sdk::frame_executive::Executive<
    Runtime,
    Block,
    polkadot_sdk::frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;
