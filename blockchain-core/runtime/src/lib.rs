#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::{
    derive_impl, parameter_types,
    traits::ConstBool,
    weights::IdentityFee,
    genesis_builder_helper::{build_state, get_preset},
};
use polkadot_sdk::frame_system;
use polkadot_sdk::pallet_aura;
use polkadot_sdk::pallet_balances;
use polkadot_sdk::pallet_grandpa;
use polkadot_sdk::pallet_sudo;
use polkadot_sdk::pallet_timestamp;
use polkadot_sdk::pallet_transaction_payment::{self, FungibleAdapter};
use polkadot_sdk::frame_executive;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId as AuraId;
use polkadot_sdk::sp_consensus_grandpa::AuthorityId as GrandpaId;
use polkadot_sdk::sp_core;
use polkadot_sdk::sp_runtime::{
    self, create_runtime_str, generic, impl_opaque_keys,
    traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, NumberFor, Verify},
    transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, MultiSignature,
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};
#[cfg(feature = "std")]
use polkadot_sdk::sp_version::NativeVersion;

pub use polkadot_sdk::frame_system::Call as SystemCall;
pub use polkadot_sdk::pallet_balances::Call as BalancesCall;
pub use polkadot_sdk::pallet_timestamp::Call as TimestampCall;

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type Nonce = u32;
pub type Hash = polkadot_sdk::sp_core::H256;
pub type BlockNumber = u32;

pub type SignedExtra = (
    frame_system::CheckNonZeroSender<Runtime>,
    frame_system::CheckSpecVersion<Runtime>,
    frame_system::CheckTxVersion<Runtime>,
    frame_system::CheckGenesis<Runtime>,
    frame_system::CheckEra<Runtime>,
    frame_system::CheckNonce<Runtime>,
    frame_system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);

pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
pub type UncheckedExtrinsic =
    generic::UncheckedExtrinsic<AccountId, RuntimeCall, Signature, SignedExtra>;
pub type SignedPayload = generic::SignedPayload<RuntimeCall, SignedExtra>;
pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;

pub mod opaque {
    use super::*;
    pub use polkadot_sdk::sp_runtime::OpaqueExtrinsic as UncheckedExtrinsic;
    pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
    pub type Block = generic::Block<Header, UncheckedExtrinsic>;
    pub type BlockId = generic::BlockId<Block>;
}

impl_opaque_keys! {
    pub struct SessionKeys {
        pub aura: Aura,
        pub grandpa: Grandpa,
    }
}

#[sp_version::runtime_version]
pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("mmeco-node"),
    impl_name: create_runtime_str!("mmeco-node"),
    authoring_version: 1,
    spec_version: 100,
    impl_version: 1,
    apis: RUNTIME_API_VERSIONS,
    transaction_version: 1,
    state_version: 1,
};

#[cfg(feature = "std")]
pub fn native_version() -> NativeVersion {
    NativeVersion { runtime_version: VERSION, can_author_with: Default::default() }
}

pub const MILLISECS_PER_BLOCK: u64 = 6000;
pub const SLOT_DURATION: u64 = MILLISECS_PER_BLOCK;
pub const EXISTENTIAL_DEPOSIT: Balance = 500;

parameter_types! {
    pub const BlockHashCount: BlockNumber = 2400;
    pub const SS58Prefix: u8 = 42;
    pub const ExistentialDeposit: Balance = EXISTENTIAL_DEPOSIT;
}

#[derive_impl(frame_system::config_preludes::SolochainDefaultConfig)]
impl frame_system::Config for Runtime {
    type Block = Block;
    type BlockHashCount = BlockHashCount;
    type AccountData = pallet_balances::AccountData<Balance>;
    type SS58Prefix = SS58Prefix;
}

impl pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Aura;
    type MinimumPeriod = polkadot_sdk::frame_support::traits::ConstU64<{ SLOT_DURATION / 2 }>;
    type WeightInfo = ();
}

impl pallet_aura::Config for Runtime {
    type AuthorityId = AuraId;
    type DisabledValidators = ();
    type MaxAuthorities = polkadot_sdk::frame_support::traits::ConstU32<32>;
    type AllowMultipleBlocksPerSlot = ConstBool<false>;
    type SlotDuration = pallet_aura::MinimumPeriodTimesTwo<Runtime>;
}

impl pallet_grandpa::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type MaxAuthorities = polkadot_sdk::frame_support::traits::ConstU32<32>;
    type MaxNominators = polkadot_sdk::frame_support::traits::ConstU32<0>;
    type MaxSetIdSessionEntries = polkadot_sdk::frame_support::traits::ConstU64<0>;
    type KeyOwnerProof = polkadot_sdk::sp_core::Void;
    type EquivocationReportSystem = ();
}

impl pallet_balances::Config for Runtime {
    type MaxLocks = polkadot_sdk::frame_support::traits::ConstU32<50>;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];
    type Balance = Balance;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ExistentialDeposit;
    type AccountStore = System;
    type WeightInfo = pallet_balances::weights::SubstrateWeight<Runtime>;
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = polkadot_sdk::frame_support::traits::ConstU32<8>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
}

impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = FungibleAdapter<Balances, ()>;
    type OperationalFeeMultiplier = polkadot_sdk::frame_support::traits::ConstU8<5>;
    type WeightToFee = IdentityFee<Balance>;
    type LengthToFee = IdentityFee<Balance>;
    type FeeMultiplierUpdate = ();
}

impl pallet_sudo::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type WeightInfo = pallet_sudo::weights::SubstrateWeight<Runtime>;
}

impl reputation::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

impl pallet_projects::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

impl pallet_governance::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

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
        RuntimeTask,
    )]
    pub struct Runtime;

    #[runtime::pallet_index(0)]
    pub type System = frame_system;
    #[runtime::pallet_index(1)]
    pub type Timestamp = pallet_timestamp;
    #[runtime::pallet_index(2)]
    pub type Aura = pallet_aura;
    #[runtime::pallet_index(3)]
    pub type Grandpa = pallet_grandpa;
    #[runtime::pallet_index(4)]
    pub type Balances = pallet_balances;
    #[runtime::pallet_index(5)]
    pub type TransactionPayment = pallet_transaction_payment;
    #[runtime::pallet_index(6)]
    pub type Sudo = pallet_sudo;
    #[runtime::pallet_index(10)]
    pub type Reputation = reputation;
    #[runtime::pallet_index(11)]
    pub type Projects = pallet_projects;
    #[runtime::pallet_index(12)]
    pub type Governance = pallet_governance;
}

impl_runtime_apis! {
    impl polkadot_sdk::sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion { VERSION }
        fn execute_block(block: Block) { Executive::execute_block(block); }
        fn initialize_block(header: &<Block as BlockT>::Header) -> sp_runtime::ExtrinsicInclusionMode {
            Executive::initialize_block(header)
        }
    }

    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata {
            polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into())
        }
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> {
            Runtime::metadata_at_version(version)
        }
        fn metadata_versions() -> polkadot_sdk::sp_std::vec::Vec<u32> {
            Runtime::metadata_versions()
        }
    }

    impl polkadot_sdk::sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> ApplyExtrinsicResult {
            Executive::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            Executive::finalize_block()
        }
        fn inherent_extrinsics(data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_std::vec::Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(block: Block, data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl polkadot_sdk::sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(
            source: TransactionSource,
            tx: <Block as BlockT>::Extrinsic,
            block_hash: <Block as BlockT>::Hash,
        ) -> TransactionValidity {
            Executive::validate_transaction(source, tx, block_hash)
        }
    }

    impl polkadot_sdk::sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            Executive::offchain_worker(header)
        }
    }

    impl polkadot_sdk::sp_consensus_aura::AuraApi<Block, AuraId> for Runtime {
        fn slot_duration() -> polkadot_sdk::sp_consensus_aura::SlotDuration {
            polkadot_sdk::sp_consensus_aura::SlotDuration::from_millis(Aura::slot_duration())
        }
        fn authorities() -> polkadot_sdk::sp_std::vec::Vec<AuraId> {
            pallet_aura::Authorities::<Runtime>::get().into_inner()
        }
    }

    impl polkadot_sdk::sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(seed: Option<polkadot_sdk::sp_std::vec::Vec<u8>>) -> polkadot_sdk::sp_std::vec::Vec<u8> {
            SessionKeys::generate(seed)
        }
        fn decode_session_keys(encoded: polkadot_sdk::sp_std::vec::Vec<u8>) -> Option<polkadot_sdk::sp_std::vec::Vec<(polkadot_sdk::sp_std::vec::Vec<u8>, polkadot_sdk::sp_core::crypto::KeyTypeId)>> {
            SessionKeys::decode_into_raw_public_keys(&encoded)
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
            _: polkadot_sdk::sp_consensus_grandpa::EquivocationProof<<Block as BlockT>::Hash, NumberFor<Block>>,
            _: polkadot_sdk::sp_consensus_grandpa::OpaqueKeyOwnershipProof,
        ) -> Option<()> { None }
        fn generate_key_ownership_proof(
            _: polkadot_sdk::sp_consensus_grandpa::SetId,
            _: GrandpaId,
        ) -> Option<polkadot_sdk::sp_consensus_grandpa::OpaqueKeyOwnershipProof> { None }
    }

    impl polkadot_sdk::frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Nonce> for Runtime {
        fn account_nonce(account: AccountId) -> Nonce {
            System::account_nonce(account)
        }
    }

    impl polkadot_sdk::pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance> for Runtime {
        fn query_info(uxt: <Block as BlockT>::Extrinsic, len: u32) -> polkadot_sdk::pallet_transaction_payment_rpc_runtime_api::RuntimeDispatchInfo<Balance> {
            TransactionPayment::query_info(uxt, len)
        }
        fn query_fee_details(uxt: <Block as BlockT>::Extrinsic, len: u32) -> polkadot_sdk::pallet_transaction_payment::FeeDetails<Balance> {
            TransactionPayment::query_fee_details(uxt, len)
        }
        fn query_weight_to_fee(weight: polkadot_sdk::sp_weights::Weight) -> Balance {
            TransactionPayment::weight_to_fee(weight)
        }
        fn query_length_to_fee(length: u32) -> Balance {
            TransactionPayment::length_to_fee(length)
        }
    }

    impl polkadot_sdk::sp_genesis_builder::GenesisBuilder<Block> for Runtime {
        fn build_state(config: polkadot_sdk::sp_std::vec::Vec<u8>) -> polkadot_sdk::sp_genesis_builder::Result {
            build_state::<RuntimeGenesisConfig>(config)
        }
        fn get_preset(id: &Option<polkadot_sdk::sp_genesis_builder::PresetId>) -> Option<polkadot_sdk::sp_std::vec::Vec<u8>> {
            get_preset::<RuntimeGenesisConfig>(id, |_| None)
        }
        fn preset_names() -> polkadot_sdk::sp_std::vec::Vec<polkadot_sdk::sp_genesis_builder::PresetId> {
            polkadot_sdk::sp_std::vec![]
        }
    }
}
