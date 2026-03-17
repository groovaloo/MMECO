//! Serviço do Nó - Configuração de Redes e Consenso (SDK 2025)
use mmeco_runtime::{RuntimeApi, Block};
use polkadot_sdk::{
    sc_service::{Configuration, TaskManager, error::Error as ServiceError, PartialComponents},
    sc_executor::WasmExecutor,
    sp_io::SubstrateHostFunctions,
};
use std::sync::Arc;

pub type FullClient = polkadot_sdk::sc_client_api::FullClient<
    Block, RuntimeApi, WasmExecutor<SubstrateHostFunctions>
>;

pub fn new_partial(config: &Configuration) -> Result<PartialComponents<
    FullClient, polkadot_sdk::sc_client_api::Backend<Block>, (),
    polkadot_sdk::sc_consensus::DefaultImportQueue<Block>,
    polkadot_sdk::sc_transaction_pool::FullPool<Block, FullClient>,
    (),
>, ServiceError> {
    let executor = WasmExecutor::<SubstrateHostFunctions>::builder().build();

    let (client, backend, keystore_container, task_manager) =
        polkadot_sdk::sc_service::new_full_parts::<Block, RuntimeApi, _>(
            config, None, Arc::new(executor),
        )?;
    let client = Arc::new(client);

    let select_chain = polkadot_sdk::sc_consensus::LongestChain::new(backend.clone());

    let transaction_pool = polkadot_sdk::sc_transaction_pool::BasicPool::new_full(
        config.transaction_pool.clone(),
        config.role.is_authority().into(),
        config.prometheus_config(),
        task_manager.spawn_essential_handle(),
        client.clone(),
    );

    let import_queue = polkadot_sdk::sc_consensus_manual_seal::import_queue(
        Box::new(client.clone()),
        &task_manager.spawn_essential_handle(),
        config.prometheus_config(),
    );

    Ok(PartialComponents {
        client, backend, task_manager, import_queue, keystore_container,
        select_chain, transaction_pool, other: (),
    })
}

pub fn new_full(config: Configuration) -> Result<TaskManager, ServiceError> {
    let sc_service::PartialComponents {
        client, backend, mut task_manager, import_queue, keystore_container,
        select_chain, transaction_pool, other: _,
    } = new_partial(&config)?;

    let mut net_config = polkadot_sdk::sc_network::config::FullNetworkConfiguration::new(&config.network);

    let (network, system_rpc_tx, tx_handler_controller, network_starter, sync_service) =
        polkadot_sdk::sc_service::build_network(polkadot_sdk::sc_service::BuildNetworkParams {
            config: &config,
            net_config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            import_queue,
            block_announce_validator_builder: None,
        })?;

    Ok(task_manager)
}
