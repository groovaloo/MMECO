//! Configuração do serviço da rede (P2P, Database, RPC).
use mmeco_runtime::{RuntimeApi, Block};
use polkadot_sdk::sc_service::{Configuration, TaskManager, error::Error as ServiceError};

pub fn new_full(config: Configuration) -> Result<TaskManager, ServiceError> {
	let sc_service::PartialComponents {
		client: _, backend: _, mut task_manager, import_queue: _, keystore_container: _,
		select_chain: _, transaction_pool: _, other: _,
	} = new_partial(&config)?;

	Ok(task_manager)
}

pub fn new_partial(config: &Configuration) -> Result<polkadot_sdk::sc_service::PartialComponents<
	polkadot_sdk::sc_client_api::FullClient<Block, RuntimeApi, polkadot_sdk::sc_executor::WasmExecutor<polkadot_sdk::sp_io::SubstrateHostFunctions>>,
	polkadot_sdk::sc_client_api::Backend<Block>,
	(),
	polkadot_sdk::sc_consensus::DefaultImportQueue<Block>,
	polkadot_sdk::sc_transaction_pool::FullPool<Block, polkadot_sdk::sc_client_api::FullClient<Block, RuntimeApi, polkadot_sdk::sc_executor::WasmExecutor<polkadot_sdk::sp_io::SubstrateHostFunctions>>>,
	(),
>, ServiceError> {
	Err(ServiceError::Other("Service.rs: Pronto para configurar componentes reais".into()))
}
