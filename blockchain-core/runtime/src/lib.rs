#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::derive_impl;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_runtime::{
    generic, traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature, ExtrinsicInclusionMode, ApplyExtrinsicResult, transaction_validity::TransactionSource,
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
    pub type Aura = polkadot_sdk::pallet_aura;
    #[runtime::pallet_index(4)]
    pub type Grandpa = polkadot_sdk::pallet_grandpa;

    #[runtime::pallet_index(5)]
    pub type Reputation = crate::pallet_reputation;
    #[runtime::pallet_index(6)]
    pub type Projects = crate::pallet_projects;
    #[runtime::pallet_index(7)]
    pub type Governance = crate::pallet_governance;
}

pub use runtime::*;

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
    type OnTimestampSet = Aura;
    type MinimumPeriod = polkadot_sdk::frame_support::traits::ConstU64<1500>;
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

impl polkadot_sdk::pallet_aura::Config for Runtime {
    type AuthorityId = polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId;
    type DisabledValidators = ();
    type MaxAuthorities = polkadot_sdk::frame_support::traits::ConstU32<32>;
    type AllowMultipleBlocksPerSlot = polkadot_sdk::frame_support::traits::ConstBool<false>;
    type SlotDuration = polkadot_sdk::pallet_timestamp::SlotDuration<Self>;
}

impl polkadot_sdk::pallet_grandpa::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type MaxAuthorities = polkadot_sdk::frame_support::traits::ConstU32<32>;
    type MaxNominators = polkadot_sdk::frame_support::traits::ConstU32<0>;
    type MaxSetIdSessionEntries = polkadot_sdk::frame_support::traits::ConstU64<0>;
    type KeyOwnerProof = polkadot_sdk::sp_core::Void;
    type EquivocationReportSystem = ();
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

    impl polkadot_sdk::sp_consensus_aura::AuraApi<Block, polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId> for Runtime {
        fn slot_duration() -> polkadot_sdk::sp_consensus_aura::SlotDuration {
            polkadot_sdk::sp_consensus_aura::SlotDuration::from_millis(3000)
        }
        fn authorities() -> Vec<polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId> {
            Aura::authorities().into_inner()
        }
    }

    impl polkadot_sdk::sp_consensus_grandpa::GrandpaApi<Block> for Runtime {
        fn grandpa_authorities() -> polkadot_sdk::sp_consensus_grandpa::AuthorityList {
            Grandpa::grandpa_authorities()
        }
        fn current_set_id() -> polkadot_sdk::sp_consensus_grandpa::SetId {
            Grandpa::current_set_id()
        }
        fn submit_report_equivocation_unsigned_extrinsic(
            _equivocation_proof: polkadot_sdk::sp_consensus_grandpa::EquivocationProof<
                <Block as BlockT>::Hash,
                BlockNumber,
            >,
            _key_owner_proof: polkadot_sdk::sp_consensus_grandpa::OpaqueKeyOwnershipProof,
        ) -> Option<()> {
            None
        }
        fn generate_key_ownership_proof(
            _set_id: polkadot_sdk::sp_consensus_grandpa::SetId,
            _authority_id: polkadot_sdk::sp_consensus_grandpa::AuthorityId,
        ) -> Option<polkadot_sdk::sp_consensus_grandpa::OpaqueKeyOwnershipProof> {
            None
        }
    }
}
