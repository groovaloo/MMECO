#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::derive_impl;
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_runtime::{
    self, create_runtime_str, generic, traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    MultiSignature, ExtrinsicInclusionMode, ApplyExtrinsicResult, transaction_validity::{TransactionSource, TransactionValidity},
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};
use polkadot_sdk::parity_scale_codec::{Encode, Decode};
use polkadot_sdk::sp_std::prelude::*;

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
    #[runtime::pallet_index(4)]
    pub type TransactionPayment = polkadot_sdk::pallet_transaction_payment;
    
    // Paletes MMECO
    #[runtime::pallet_index(5)]
    pub type Reputation = reputation;
    #[runtime::pallet_index(6)]
    pub type Projects = pallet_projects;
    #[runtime::pallet_index(7)]
    pub type Governance = pallet_governance;
}

// A MÁGICA ACONTECE AQUI: Exportamos o que está dentro do 'mod runtime' para o resto do ficheiro!
pub use runtime::*;

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
