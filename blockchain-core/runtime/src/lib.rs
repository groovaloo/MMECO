#![cfg_attr(not(feature = "std"), no_std)]

use frame_support::traits::Everything;
use frame_support::parameter_types;
use sp_runtime::{
    generic, traits::{BlakeTwo256, IdentityLookup},
    MultiSignature, MultiAddress,
};

pub use reputation;
pub use pallet_projects;

pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<
    MultiAddress<sp_core::sr25519::Public, ()>,
    RuntimeCall,
    MultiSignature,
    (),
>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;

parameter_types! {
    pub const BlockHashCount: BlockNumber = 250;
    pub const SS58Prefix: u8 = 42;
    pub const Version: sp_version::RuntimeVersion = sp_version::RuntimeVersion {
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
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = BlockHashCount;
    type Version = Version;
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = SS58Prefix;
    type OnSetCode = ();
    type MaxConsumers = frame_support::traits::ConstU32<16>;
    type RuntimeTask = ();
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl reputation::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
}

impl pallet_projects::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Reputation = Runtime;
}

frame_support::construct_runtime!(
    pub enum Runtime {
        System: frame_system,
        Reputation: reputation,
        Projects: pallet_projects,
    }
);

pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;

