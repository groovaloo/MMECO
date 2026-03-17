#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::derive_impl;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_runtime::{
    self, create_runtime_str, generic, traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature, ExtrinsicInclusionMode,
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};
use polkadot_sdk::parity_scale_codec::{Encode, Decode};

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;

// No Polkadot SDK moderno, simplificamos o SignedExtra para evitar erros de Encode
pub type SignedExtra = (
    polkadot_sdk::frame_system::CheckNonZeroSender<Runtime>,
    polkadot_sdk::frame_system::CheckSpecVersion<Runtime>,
    polkadot_sdk::frame_system::CheckTxVersion<Runtime>,
    polkadot_sdk::frame_system::CheckGenesis<Runtime>,
    polkadot_sdk::frame_system::CheckEra<Runtime>,
    polkadot_sdk::frame_system::CheckNonce<Runtime>,
    polkadot_sdk::frame_system::CheckWeight<Runtime>,
    polkadot_sdk::pallet_balances::ChargeTransactionPayment<Runtime>,
);

pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<AccountId, RuntimeCall, Signature, SignedExtra>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;

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
    pub type Balances = polkadot_sdk::pallet_balances;
    #[runtime::pallet_index(3)]
    pub type Sudo = polkadot_sdk::pallet_sudo;
    
    // As tuas paletes personalizadas
    #[runtime::pallet_index(4)]
    pub type Reputation = reputation;
    #[runtime::pallet_index(5)]
    pub type Projects = pallet_projects;
    #[runtime::pallet_index(6)]
    pub type Governance = pallet_governance;
}

#[derive_impl(polkadot_sdk::frame_system::config_preludes::SolochainDefaultConfig)]
impl polkadot_sdk::frame_system::Config for Runtime {
    type Block = Block;
    type AccountData = polkadot_sdk::pallet_balances::AccountData<Balance>;
}

// Configuração das tuas paletes
impl reputation::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
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

impl polkadot_sdk::pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = polkadot_sdk::pallet_transaction_payment::FungibleAdapter<Balances, ()>;
    type OperationalFeeMultiplier = polkadot_sdk::frame_support::traits::ConstU8<5>;
    type WeightToFee = polkadot_sdk::frame_support::weights::IdentityFee<Balance>;
    type LengthToFee = polkadot_sdk::frame_support::weights::IdentityFee<Balance>;
    type FeeMultiplierUpdate = ();
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
        fn initialize_block(header: &<Block as BlockT>::Header) -> ExtrinsicInclusionMode {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime,
