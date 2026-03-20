#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

extern crate alloc;

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use alloc::vec::Vec;
use polkadot_sdk::sp_std::borrow::Cow;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_runtime::{
    generic, 
    traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature,
};
use polkadot_sdk::sp_version::RuntimeVersion;

pub use pallet_reputation;
pub use pallet_projects;
pub use pallet_governance;

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Hash = polkadot_sdk::sp_core::H256;
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
mod runtime_impl {
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

pub use runtime_impl::Runtime;
pub use runtime_impl::{RuntimeCall, RuntimeEvent, RuntimeOrigin, RuntimeTask};
pub use runtime_impl::{RuntimeFreezeReason, RuntimeHoldReason};

impl polkadot_sdk::frame_system::Config for Runtime {
    type Block = Block;
    type AccountData = polkadot_sdk::pallet_balances::AccountData<Balance>;
    type BaseCallFilter = polkadot_sdk::frame_support::traits::Everything;
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type RuntimeTask = RuntimeTask;
    type Hash = Hash;
    type Hashing = BlakeTwo256;
    type AccountId = AccountId;
    type Lookup = polkadot_sdk::sp_runtime::traits::AccountIdLookup<AccountId, ()>;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = polkadot_sdk::frame_support::traits::ConstU32<256>;
    type DbWeight = ();
    type Version = ();
    type PalletInfo = polkadot_sdk::frame_support::traits::PalletInfoAccess;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type BlockWeights = ();
    type BlockLength = ();
    type SS58Prefix = polkadot_sdk::frame_support::traits::ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = polkadot_sdk::frame_support::traits::ConstU32<16>;
    type Nonce = u32;
    type ExtensionsWeightInfo = ();
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl pallet_reputation::Config for Runtime { 
    type RuntimeEvent = RuntimeEvent; 
}

impl pallet_projects::Config for Runtime { 
    type RuntimeEvent = RuntimeEvent; 
}

impl pallet_governance::Config for Runtime { 
    type RuntimeEvent = RuntimeEvent; 
}

impl polkadot_sdk::pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = polkadot_sdk::pallet_aura::Pallet<Runtime>;
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
    type AccountStore = polkadot_sdk::frame_system::Pallet<Runtime>;
    type WeightInfo = ();
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = polkadot_sdk::frame_support::traits::ConstU32<8>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
    type DoneSlashHandler = ();
}

impl polkadot_sdk::pallet_aura::Config for Runtime {
    type AuthorityId = polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId;
    type DisabledValidators = ();
    type MaxAuthorities = polkadot_sdk::frame_support::traits::ConstU32<32>;
    type AllowMultipleBlocksPerSlot = polkadot_sdk::frame_support::traits::ConstBool<false>;
    type SlotDuration = polkadot_sdk::pallet_aura::MinimumPeriodTimesTwo<Runtime>;
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
    apis: polkadot_sdk::sp_version::create_apis_vec!([]),
    transaction_version: 1,
    system_version: 1,
};

impl_runtime_apis! {
    impl polkadot_sdk::sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion { 
            VERSION 
        }
        
        fn execute_block(block: Block) { 
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::execute_block(block); 
        }
        
        fn initialize_block(header: &Header) -> polkadot_sdk::sp_runtime::ExtrinsicInclusionMode {
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::initialize_block(header)
        }
    }

    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata { 
            polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into()) 
        }
        
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> { 
            Runtime::metadata_at_version(version) 
        }
        
        fn metadata_versions() -> Vec<u32> { 
            Runtime::metadata_versions() 
        }
    }

    impl polkadot_sdk::sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> polkadot_sdk::sp_runtime::ApplyExtrinsicResult {
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::apply_extrinsic(extrinsic)
        }
        
        fn finalize_block() -> Header {
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::finalize_block()
        }
        
        fn inherent_extrinsics(data: polkadot_sdk::sp_inherents::InherentData) -> Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        
        fn check_inherents(
            block: Block, 
            data: polkadot_sdk::sp_inherents::InherentData
        ) -> polkadot_sdk::sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl polkadot_sdk::sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(
            source: polkadot_sdk::sp_runtime::transaction_validity::TransactionSource,
            tx: <Block as BlockT>::Extrinsic, 
            block_hash: Hash
        ) -> polkadot_sdk::sp_runtime::transaction_validity::TransactionValidity {
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::validate_transaction(source, tx, block_hash)
        }
    }

    impl polkadot_sdk::sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &Header) {
            polkadot_sdk::frame_executive::Executive::
                Runtime, 
                Block, 
                polkadot_sdk::frame_system::ChainContext<Runtime>, 
                Runtime, 
                runtime_impl::AllPalletsWithSystem
            >::offchain_worker(header)
        }
    }

    impl polkadot_sdk::sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(_seed: Option<Vec<u8>>) -> Vec<u8> { 
            Default::default() 
        }
        
        fn decode_session_keys(
            _encoded: Vec<u8>
        ) -> Option<Vec<(Vec<u8>, polkadot_sdk::sp_core::crypto::KeyTypeId)>> { 
            None 
        }
    }

    impl polkadot_sdk::sp_consensus_aura::AuraApi<Block, polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId> for Runtime {
        fn slot_duration() -> polkadot_sdk::sp_consensus_aura::SlotDuration {
            polkadot_sdk::sp_consensus_aura::SlotDuration::from_millis(3000)
        }
        
        fn authorities() -> Vec<polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId> {
            use polkadot_sdk::frame_support::traits::Get;
            polkadot_sdk::pallet_aura::Authorities::<Runtime>::get().to_vec()
        }
    }

    impl polkadot_sdk::sp_consensus_grandpa::GrandpaApi<Block> for Runtime {
        fn grandpa_authorities() -> polkadot_sdk::sp_consensus_grandpa::AuthorityList {
            polkadot_sdk::pallet_grandpa::Pallet::<Runtime>::grandpa_authorities()
        }
        
        fn current_set_id() -> polkadot_sdk::sp_consensus_grandpa::SetId {
            polkadot_sdk::pallet_grandpa::Pallet::<Runtime>::current_set_id()
        }
        
        fn submit_report_equivocation_unsigned_extrinsic(
            _equivocation_proof: polkadot_sdk::sp_consensus_grandpa::EquivocationProof
                Hash,
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
