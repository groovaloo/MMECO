use clap::Parser;
use jsonrpsee::server::{RpcModule, Server};
use jsonrpsee::core::RpcResult;
use serde_json::{json, Value};
use tokio::signal;

#[derive(Parser, Debug)]
#[command(author, version, about = "Moral Money Node", long_about = None)]
struct Cli {
    #[arg(long, default_value = "moral-money-node")]
    name: String,
    #[arg(long)]
    dev: bool,
    #[arg(long)]
    validator: bool,
    #[arg(long, default_value = "9933")]
    rpc_port: u16,
    #[arg(long, default_value = "9944")]
    ws_port: u16,
    #[arg(long)]
    rpc_external: bool,
    #[arg(long)]
    ws_external: bool,
    #[arg(long, default_value = "all")]
    rpc_cors: String,
    #[arg(long)]
    tmp: bool,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    println!("=== MORAL MONEY NODE ===");
    println!("Nome:        {}", cli.name);
    println!("Dev mode:    {}", cli.dev);
    println!("Validador:   {}", cli.validator);
    println!("RPC porta:   {}", cli.rpc_port);
    println!("WS porta:    {}", cli.ws_port);
    println!("Pallets:     Reputation, Projects, Governance");
    println!("========================");

    // Servidor RPC/WS
    let ws_addr = format!("0.0.0.0:{}", cli.ws_port);
    let server = Server::builder()
        .build(&ws_addr)
        .await?;

    let mut module = RpcModule::new(());

    // system_health
    module.register_method("system_health", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!({
            "isSyncing": false,
            "peers": 0,
            "shouldHavePeers": false
        }))
    })?;

    // system_name
    module.register_method("system_name", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!("Moral Money Node"))
    })?;

    // system_version
    module.register_method("system_version", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!("0.1.0"))
    })?;

    // chain_getHeader
    module.register_method("chain_getHeader", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!({
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "number": "0x0",
            "stateRoot": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "extrinsicsRoot": "0x0000000000000000000000000000000000000000000000000000000000000000"
        }))
    })?;

    // chain_getBlockHash
    module.register_method("chain_getBlockHash", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!("0x0000000000000000000000000000000000000000000000000000000000000000"))
    })?;

    // rpc_methods
    module.register_method("rpc_methods", |_, _, _| {
        Ok::<Value, jsonrpsee::types::ErrorObjectOwned>(json!({
            "version": 1,
            "methods": [
                "system_health",
                "system_name",
                "system_version",
                "chain_getHeader",
                "chain_getBlockHash",
                "rpc_methods"
            ]
        }))
    })?;

    let addr = server.local_addr()?;
    let handle = server.start(module);

    println!("✅ RPC/WS activo em ws://{}", addr);
    println!("✅ Node pronto. Ctrl+C para parar.");

    signal::ctrl_c().await?;
    println!("🛑 Node a parar...");
    handle.stop()?;

    Ok(())
}
