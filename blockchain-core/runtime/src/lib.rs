#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::derive_impl;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_runtime::{
    generic, traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature, ExtrinsicInclusionMode, ApplyExtrinsicResult, transaction_validity::{TransactionSource, TransactionValidity},
};
use polkadot_sdk::sp_version::RuntimeVersion;
use polkadot_sdk::sp_std::prelude::*;
use polkadot_sdk::sp_std::borrow::Cow;

pub use pallet_reputation;
pub use pallet_projects;
pub use pallet_governance;

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;

// REMOVIDA A PORTAGEM (ChargeTransactionPayment) PORQUE TIRÁMOS A PALETE DAS TAXAS
pub type SignedExtra = (
    polkadot_sdk::frame_system::CheckNonZeroSender<Runtime>,
    polkadot_sdk::frame_system::CheckSpecVersion<Runtime>,
    polkadot_sdk::frame_system::CheckTxVersion<Runtime>,
    polkadot_sdk::frame_system::CheckGenesis<Runtime>,
    polkadot_sdk::frame_system::CheckEra<Runtime>,
    polkadot_sdk::frame_system::CheckNonce<Runtime>,
    polkadot_sdk::frame_system::CheckWeight<Runtime>,
);

pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<AccountId, RuntimeCall, Signature, SignedExtra>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;

#[polkadot_sdk::frame_support::runtime]
pub mod runtime {
    #[runtime::runtime]
    #[runtime::derive(
        RuntimeCall, RuntimeEvent, RuntimeError, RuntimeOrigin,
        RuntimeFreezeReason, RuntimeHoldReason, RuntimeSlashReason,
        RuntimeLockId, RuntimeTask,
    )]
    pub struct Runtime;

    #[runtime::pallet_index(0)]
    pub type System = polkadot_sdk::frame_system;
    #[runtime::pallet_index(1)]
    pub type Timestamp = polkadot_sdk::pallet_timestamp;
    #[runtime::pallet_index(2)]
    pub type Balances = polkadot_sdk::pallet_balances;
    #[runtime::pallet_index(3)]
    pub type Sudo = polkadot_sdk::pallet_sudo;
    
    // AS 3 PALETES MMECO
    #[runtime::pallet_index(4)]
    pub type Reputation = crate::pallet_reputation;
    #[runtime::pallet_index(5)]
    pub type Projects = crate::pallet_projects;
    #[runtime::pallet_index(6)]
    pub type Governance = crate::pallet_governance;
}

// A CHAVE MÁGICA QUE ABRE A PORTA (Resolve os erros E0412 e E0433)
pub use crate::runtime::*;

#[derive_impl(polkadot_sdk::frame_system::config_preludes::SolochainDefaultConfig)]
impl polkadot_sdk::frame_system::Config for Runtime {
    type Block = Block;
    type AccountData = polkadot_sdk::pallet_balances::AccountData<Balance>;
}

impl pallet_reputation::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
impl pallet_projects::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
impl pallet_governance::Config for Runtime { type RuntimeEvent = RuntimeEvent; }

impl polkadot_sdk::pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = ();
    type MinimumPeriod = polkadot_sdk::frame_support::traits::ConstU64<3000>;
    type WeightInfo = ();
}

impl polkadot_sdk::pallet_balances::Config for Runtime {
    type MaxLocks = polkadot_sdk::frame_support::traits::ConstU32<50>;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];
    type Balance = Balance;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = polkadot_sdk::frame_support::traits::ConstU128<500>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = polkadot_sdk::frame_support::traits::ConstU32<8>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
}

impl polkadot_sdk::pallet_sudo::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type WeightInfo = ();
}

pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: Cow::Borrowed("moral-money"),
    impl_name: Cow::Borrowed("moral-money"),
    authoring_version: 1,
    spec_version: 1,
    impl_version: 1,
    apis: RUNTIME_API_VERSIONS,
    transaction_version: 1,
    state_version: 1,
};

impl_runtime_apis! {
    impl polkadot_sdk::sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion { VERSION }
        fn execute_block(block: Block) { 
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::execute_block(block); 
        }
        fn initialize_block(header: &<Block as BlockT>::Header) -> ExtrinsicInclusionMode {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::initialize_block(header)
        }
    }

    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata { polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into()) }
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> { Runtime::metadata_at_version(version) }
        fn metadata_versions() -> polkadot_sdk::sp_std::vec::Vec<u32> { Runtime::metadata_versions() }
    }

    impl polkadot_sdk::sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> ApplyExtrinsicResult {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::finalize_block()
        }
        fn inherent_extrinsics(data: polkadot_sdk::sp_inherents::InherentData) -> Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(block: Block, data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl polkadot_sdk::sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(source: TransactionSource, tx: <Block as BlockT>::Extrinsic, block_hash: <Block as BlockT>::Hash) -> polkadot_sdk::sp_runtime::transaction_validity::TransactionValidity {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::validate_transaction(source, tx, block_hash)
        }
    }

    impl polkadot_sdk::sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::offchain_worker(header)
        }
    }

    impl polkadot_sdk::sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(_seed: Option<Vec<u8>>) -> Vec<u8> { Default::default() }
        fn decode_session_keys(_encoded: Vec<u8>) -> Option<Vec<(Vec<u8>, polkadot_sdk::sp_core::crypto::KeyTypeId)>> { None }
    }
}
