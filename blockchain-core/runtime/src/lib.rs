#![cfg_attr(not(feature = "std"), no_std)]

use frame_support::{
    parameter_types,
    traits::{Everything, ConstU32},
};
use sp_runtime::{
    generic, traits::{BlakeTwo256, IdentityLookup},
    MultiSignature, MultiAddress, create_runtime_str,
};
use sp_std::prelude::*;

pub use reputation;

parameter_types! {
    pub const BlockHashCount: u32 = 250;
    pub const SS58Prefix: u8 = 42;
    pub const RuntimeVersion: sp_version::RuntimeVersion = sp_version::RuntimeVersion {
        spec_name: create_runtime_str!("moral-money"),
        impl_name: create_runtime_str!("moral-money"),
        authoring_version: 1,
        spec_version: 1,
        impl_version: 1,
        apis: sp_version::create_apis_vec!([]),
        transaction_version: 1,
        state_version: 1,
    };
}

#[frame_support::runtime]
pub mod runtime {
    #[runtime::runtime]
    #[runtime::derive(
        RuntimeCall, 
        RuntimeEvent, 
        RuntimeError, 
        RuntimeOrigin, 
        RuntimeFreezeReason, 
        RuntimeHoldReason, 
        RuntimeSlashReason, 
        RuntimeTask
    )]
    pub struct Runtime;

    #[runtime::pallet_index(0)]
    pub type System = frame_system;

    #[runtime::pallet_index(1)]
    pub type Reputation = reputation;
}

impl frame_system::Config for Runtime {
    type BaseCallFilter = Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u32;
    type Hash = sp_core::H256;
    type Hashing = BlakeTwo256;
    type AccountId = sp_core::sr25519::Public;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = generic::Block<generic::Header<u32, BlakeTwo256>, generic::UncheckedExtrinsic<MultiAddress<Self::AccountId, ()>, RuntimeCall, MultiSignature, ()>>;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = BlockHashCount;
    type Version = RuntimeVersion;
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = SS58Prefix;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type RuntimeTask = RuntimeTask;
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl reputation::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}