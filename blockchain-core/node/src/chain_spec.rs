use mmeco_runtime::{AccountId, RuntimeGenesisConfig, WASM_BINARY, Signature};
use polkadot_sdk::sc_service::ChainType;
use polkadot_sdk::sp_core::{sr25519, Pair, Public};
use polkadot_sdk::sp_runtime::traits::{IdentifyAccount, Verify};

/// Especialização da Spec da Chain
pub type ChainSpec = polkadot_sdk::sc_service::GenericChainSpec<RuntimeGenesisConfig>;

fn get_from_seed<TPublic: Public>(seed: &str) -> <TPublic::Pair as Pair>::Public {
	TPublic::Pair::from_string(&format!("//{}", seed), None)
		.expect("Seed inválida")
		.public()
}

type AccountPublic = <Signature as Verify>::Signer;

pub fn get_account_id_from_seed<TPublic: Public>(seed: &str) -> AccountId
where
	AccountPublic: From<<TPublic::Pair as Pair>::Public>,
{
	AccountPublic::from(get_from_seed::<TPublic>(seed)).into_account()
}

pub fn development_config() -> Result<ChainSpec, String> {
	let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary não disponível".to_string())?;

	Ok(ChainSpec::from_genesis(
		"Development",
		"dev",
		ChainType::Development,
		move || {
			testnet_genesis(
				wasm_binary,
				// Root Key (Sudo) - Alice
				get_account_id_from_seed::<sr25519::Public>("Alice"),
				vec![
					get_account_id_from_seed::<sr25519::Public>("Alice"),
					get_account_id_from_seed::<sr25519::Public>("Bob"),
				],
			)
		},
		vec![],
		None,
		None,
		None,
		None,
		None,
	))
}

fn testnet_genesis(
	wasm_binary: &[u8],
	root_key: AccountId,
	endowed_accounts: Vec<AccountId>,
) -> RuntimeGenesisConfig {
	RuntimeGenesisConfig {
		system: polkadot_sdk::frame_system::GenesisConfig {
			code: wasm_binary.to_vec(),
			..Default::default()
		},
		balances: polkadot_sdk::pallet_balances::GenesisConfig {
			balances: endowed_accounts.iter().cloned().map(|k| (k, 1 << 60)).collect(),
		},
		sudo: polkadot_sdk::pallet_sudo::GenesisConfig {
			key: Some(root_key),
		},
		transaction_payment: Default::default(),
		reputation: Default::default(),
		pallet_projects: Default::default(),
		pallet_governance: Default::default(),
	}
}
