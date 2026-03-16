#![cfg_attr(not(feature = "std"), no_std)]
#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use polkadot_sdk::frame_support::{
    derive_impl, parameter_types, traits::ConstBool, weights::IdentityFee,
    genesis_builder_helper::{build_state, get_preset},
};
use polkadot_sdk::sp_api::impl_runtime_apis;
use polkadot_sdk::sp_consensus_aura::sr25519::AuthorityId as AuraId;
use polkadot_sdk::sp_consensus_grandpa::AuthorityId as GrandpaId;
use polkadot_sdk::sp_core::{self, Encode, Decode};
use polkadot_sdk::sp_runtime::{
    self, create_runtime_str, generic, impl_opaque_keys, RuntimeDebug,
    traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, NumberFor, Verify},
    transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, MultiSignature,
};
use polkadot_sdk::sp_version::{self, RuntimeVersion};
#[cfg(feature = "std")]
use polkadot_sdk::sp_version::NativeVersion;

pub type Signature = MultiSignature;
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;
pub type Balance = u128;
pub type Nonce = u32;
pub type Hash = polkadot_sdk::sp_core::H256;
pub type BlockNumber = u32;

// CORREÇÃO: Adicionando derivações explícitas para o sistema de tipos de 2025
#[derive(Encode, Decode, RuntimeDebug, Clone, PartialEq, Eq, polkadot_sdk::scale_info::TypeInfo)]
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

    // Pallets customizadas da Moral Money
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

// Implementações mínimas para as tuas pallets
impl reputation::Config for Runtime { type RuntimeEvent = RuntimeEvent; }
impl pallet_projects::Config for Runtime { type RuntimeEvent = RuntimeEvent; type Reputation = Runtime; }
impl pallet_governance::Config for Runtime { type RuntimeEvent = RuntimeEvent; }

// Restantes Configs (Aura, Balances, etc. mantêm-se como tinhas)
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

// Bloco de APIs (Simplificado para garantir a compilação)
impl_runtime_apis! {
    impl polkadot_sdk::sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion { VERSION }
        fn execute_block(block: Block) { polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::execute_block(block); }
        fn initialize_block(header: &<Block as BlockT>::Header) -> polkadot_sdk::sp_runtime::ExtrinsicInclusionMode {
            polkadot_sdk::frame_executive::Executive::<Runtime, Block, polkadot_sdk::frame_system::ChainContext<Runtime>, Runtime, AllPalletsWithSystem>::initialize_block(header)
        }
    }
    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata { polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into()) }
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> { Runtime::metadata_at_version(version) }
        fn metadata_versions() -> polkadot_sdk::sp_std::vec::Vec<u32> { Runtime::metadata_versions() }
    }
    // ... (restantes APIs mantêm o padrão)
}
