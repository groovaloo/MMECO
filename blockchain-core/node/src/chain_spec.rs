use mmeco_runtime::{AccountId, RuntimeGenesisConfig, WASM_BINARY};
use polkadot_sdk::sc_service::ChainType;

/// Especialização da Spec da Chain
pub type ChainSpec = polkadot_sdk::sc_service::GenericChainSpec<RuntimeGenesisConfig>;

pub fn development_config() -> Result<ChainSpec, String> {
	let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary não disponível".to_string())?;

	Ok(ChainSpec::from_genesis(
		"Development",
		"dev",
		ChainType::Development,
		move || {
			testnet_genesis(
				wasm_binary,
				// Root Key (Sudo) - Usamos a conta de teste Alice
				hex_literal::hex!("d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d").into(),
				vec![
					hex_literal::hex!("d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d").into(),
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
        // As tuas paletes iniciam vazias por defeito
		reputation: Default::default(),
		pallet_projects: Default::default(),
		pallet_governance: Default::default(),
	}
}
