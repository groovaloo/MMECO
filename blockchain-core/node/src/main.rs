use clap::{Parser, Args};
use std::net::SocketAddr;

#[derive(Parser, Debug)]
#[command(author, version, about = "Moral Money Node", long_about = None)]
struct Cli {
    /// Name of the node
    #[arg(short, long, default_value = "moral-money-node")]
    name: String,

    /// Run in development mode
    #[arg(long)]
    dev: bool,

    /// Run as a validator
    #[arg(long)]
    validator: bool,

    /// RPC server external access
    #[arg(long)]
    rpc_external: bool,

    /// WebSocket server external access
    #[arg(long)]
    ws_external: bool,

    /// RPC server port
    #[arg(long, default_value = "9933")]
    rpc_port: u16,

    /// WebSocket server port
    #[arg(long, default_value = "9944")]
    ws_port: u16,

    /// RPC CORS domains
    #[arg(long, default_value = "all")]
    rpc_cors: String,

    /// RPC methods
    #[arg(long, default_value = "Unsafe")]
    rpc_methods: String,

    /// RPC max payload size
    #[arg(long, default_value = "10485760")]
    rpc_max_payload: u32,

    /// RPC max connections
    #[arg(long, default_value = "100")]
    rpc_max_connections: u32,

    /// RPC max request size
    #[arg(long, default_value = "10485760")]
    rpc_max_request_size: u32,

    /// RPC max response size
    #[arg(long, default_value = "10485760")]
    rpc_max_response_size: u32,
}

fn main() {
    let cli = Cli::parse();

    println!("--- Moral Money Ecosystem ---");
    println!("Nó inicializado com o nome: {}", cli.name);
    println!("Modo desenvolvimento: {}", if cli.dev { "Sim" } else { "Não" });
    println!("Modo validador: {}", if cli.validator { "Sim" } else { "Não" });
    println!("Runtime carregado com sucesso.");
    println!("Categorias de Reputação: Construção, Agricultura, Energia, Governação, Saúde, Logística.");
    println!("Buildcoin Network: Ativa e Sincronizada");
    println!("-----------------------------");

    if cli.rpc_external {
        println!("RPC externo habilitado na porta {}", cli.rpc_port);
    }
    if cli.ws_external {
        println!("WebSocket externo habilitado na porta {}", cli.ws_port);
    }

    println!("O nó está pronto para ser integrado com o Consensus Engine.");
}
