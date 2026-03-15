use sc_service::ChainType;
use sp_core::{sr25519::Public, Pair, Public as _};
use runtime::{AccountId, Signature, WASM_BINARY};
use sp_runtime::traits::{Verify, IdentifyAccount};

pub type ChainSpec = sc_service::GenericChainSpec<runtime::GenesisConfig>;

fn get_from_seed<TPublic: Public>(seed: &str) -> TPublic {
	TPublic::Pair::from_string(&format!("//{}", seed), None)
		.expect("static values are valid; qed")
		.public()
}

type AccountPublic = <Signature as Verify>::Signer;

pub fn account_id_from_seed<TPublic: Public>(seed: &str) -> AccountId {
	AccountPublic::from_seed::<TPublic>(seed).into_account()
}

pub fn development_config() -> Result<ChainSpec, String> {
	let wasm_binary = WASM_BINARY.ok_or_else(|| "Development wasm not available".to_string())?;

	Ok(ChainSpec::from_genesis(
		"Development",
		"dev",
		ChainType::Development,
		move || testnet_genesis(
			wasm_binary,
			get_from_seed::<Public>("Alice"),
			vec![],
			account_id_from_seed::<Public>("Alice"),
		),
		vec![],
		None,
		None,
		None,
		None,
		None,
	))
}

fn testnet_genesis(
	wasm_binary: Vec<u8>,
	root_key: AccountId,
	initial_authorities: Vec<(Public, Public)>,
	_endowed_accounts: AccountId,
) -> runtime::GenesisConfig {
	runtime::GenesisConfig {
		system: runtime::SystemConfig {
			code: wasm_binary,
		},
		balances: runtime::BalancesConfig {
			balances: vec![(root_key.clone(), 1 << 60)],
		},
		aura: runtime::AuraConfig {
			authorities: initial_authorities.into_iter().map(|x| x.0).collect(),
		},
		grandpa: runtime::GrandpaConfig {
			authorities: vec![],
		},
		sudo: runtime::SudoConfig {
			key: Some(root_key),
		},
		transaction_payment: Default::default(),
	}
}
