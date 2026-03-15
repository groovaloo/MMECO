#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

// Inclui o binário WASM
#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::{
    construct_runtime, derive_impl, parameter_types, traits::Everything,
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

// Corrigido para o padrão 2025
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<
    MultiAddress<sp_core::sr25519::Public, ()>,
    RuntimeCall,
    MultiSignature,
    SignedExtra,
>;

pub type SignedExtra = (); 
pub type Block = generic::Block<Header, UncheckedExtrinsic>;

parameter_types! {
    pub const BlockHashCount: BlockNumber = 250;
    pub const SS58Prefix: u8 = 42;
    pub const Version: RuntimeVersion = RuntimeVersion {
        spec_name: sp_version::create_runtime_str!("moral-money"),
        impl_name: sp_version::create_runtime_str!("moral-money"),
        authoring_version: 1,
        spec_version: 1,
        impl_version: 1,
        apis: sp_version::create_apis_vec!([]),
        transaction_version: 1,
        state_version: 1,
    };
}

// Implementação moderna do System
#[derive_impl(frame_system::config_preludes::SolochainDefaultConfig)]
impl frame_system::Config for Runtime {
    type Block = Block;
    type AccountId = sp_core::sr25519::Public;
    type Lookup = IdentityLookup<Self::AccountId>;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type RuntimeOrigin = RuntimeOrigin;
    type Version = Version;
    type SS58Prefix = SS58Prefix;
    type MaxConsumers = polkadot_sdk::frame_support::traits::ConstU32<16>;
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

// A macro obrigatória para o SDK 2025
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
    pub type System = frame_system::Pallet<Runtime>;

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
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;
