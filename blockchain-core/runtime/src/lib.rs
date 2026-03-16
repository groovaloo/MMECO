#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::derive_impl;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId as AuraId;
use polkadot_sdk::sp_core::{self, Encode, Decode};
use polkadot_sdk::sp_runtime::{
    self, create_runtime_str, generic, impl_opaque_keys, traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature,
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type BlockNumber = u32;

impl_opaque_keys! {
    pub struct SessionKeys {
        pub aura: Aura,
        pub grandpa: Grandpa,
    }
}

#[derive(Encode, Decode, polkadot_sdk::sp_runtime::RuntimeDebug, Clone, PartialEq, Eq, polkadot_sdk::scale_info::TypeInfo)]
pub struct SignedExtra;

impl polkadot_sdk::sp_runtime::traits::SignedExtension for SignedExtra {
    const IDENTIFIER: &'static str = "SignedExtra";
    type AccountId = AccountId;
    type Call = RuntimeCall;
    type AdditionalSigned = ();
    type Pre = ();
    fn additional_signed(&self) -> Result<Self::AdditionalSigned, polkadot_sdk::sp_runtime::transaction_validity::TransactionValidityError> { Ok(()) }
    fn pre_dispatch(self, _who: &Self::AccountId, _call: &Self::Call, _info: &polkadot_sdk::sp_runtime::traits::DispatchInfoOf<Self::Call>, _len: usize) -> Result<Self::Pre, polkadot_sdk::sp_runtime::transaction_validity::TransactionValidityError> { Ok(()) }
}

pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type UncheckedExtrinsic = polkadot_sdk::sp_runtime::generic::UncheckedExtrinsic<AccountId, RuntimeCall, Signature, SignedExtra>;
pub type Block = polkadot_sdk::sp_runtime::generic::Block<Header, UncheckedExtrinsic>;

#[polkadot_sdk::frame_support::runtime]
mod runtime {
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
    pub type Aura = polkadot_sdk::pallet_aura;
    #[runtime::pallet_index(3)]
    pub type Grandpa = polkadot_sdk::pallet_grandpa;
    #[runtime::pallet_index(4)]
    pub type Balances = polkadot_sdk::pallet_balances;
    #[runtime::pallet_index(5)]
    pub type TransactionPayment = polkadot_sdk::pallet_transaction_payment;
    #[runtime::pallet_index(6)]
    pub type Sudo = polkadot_sdk::pallet_sudo;

    #[runtime::pallet_index(10)]
    pub type Reputation = reputation;
    #[runtime::pallet_index(11)]
    pub type Projects = pallet_projects;
    #[runtime::pallet_index(12)]
    pub type Governance = pallet_governance;
}

#[derive_impl(polkadot_sdk::frame_system::config_preludes::SolochainDefaultConfig)]
impl polkadot_sdk::frame_system::Config for Runtime {
    type Block = Block;
    type AccountData = polkadot_sdk::pallet_balances::AccountData<Balance>;
}

impl reputation::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
impl pallet_projects::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
impl pallet_governance::Config for Runtime { type RuntimeEvent = RuntimeEvent; }

impl polkadot_sdk::pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Aura;
    type MinimumPeriod = polkadot_sdk::frame_support::traits::ConstU64<3000>;
    type WeightInfo = ();
}

impl polkadot_sdk::pallet_aura::Config for Runtime {
    type AuthorityId = AuraId;
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

impl polkadot_sdk::pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = polkadot_sdk::pallet_transaction_payment::FungibleAdapter<Balances, ()>;
    type OperationalFeeMultiplier = polkadot_sdk::frame_support::traits::ConstU8<5>;
    type WeightToFee = polkadot_sdk::frame_support::weights::IdentityFee<Balance>;
    type LengthToFee = polkadot_sdk::frame_support::weights::IdentityFee<Balance>;
    type FeeMultiplierUpdate = ();
}

impl polkadot_sdk::pallet_sudo::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type WeightInfo = ();
}

pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("moral-money"),
    impl_name: create_runtime_str!("moral-money"),
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
        fn initialize_block(header: &<Block as BlockT>::Header) -> polkadot_sdk::sp_runtime::ExtrinsicInclusionMode {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::initialize_block(header)
        }
    }
    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata { polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into()) }
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> { Runtime::metadata_at_version(version) }
        fn metadata_versions() -> polkadot_sdk::sp_std::vec::Vec<u32> { Runtime::metadata_versions() }
    }
    impl polkadot_sdk::sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> polkadot_sdk::sp_runtime::ApplyExtrinsicResult {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::finalize_block()
        }
        fn inherent_extrinsics(data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_std::vec::Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(block: Block, data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }
}
