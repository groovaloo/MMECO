//! Nó Moral Money - Reconstrução Polkadot SDK 2025
//! Este ficheiro inicia o serviço real da blockchain, ligando o Runtime e as Paletes.

use clap::Parser;
use polkadot_sdk::sc_cli::{SubstrateCli, RuntimeVersion, ChainSpec};

// Estrutura de CLI do Substrate Moderno
#[derive(Parser, Debug)]
pub struct Cli {
	#[command(subcommand)]
	pub subcommand: Option<Subcommand>,

	#[clap(flatten)]
	pub run: polkadot_sdk::sc_cli::RunCmd,
}

#[derive(Parser, Debug)]
pub enum Subcommand {
	/// Limpa a base de dados
	PurgeChain(polkadot_sdk::sc_cli::PurgeChainCmd),
	/// Exporta o estado para JSON
	CheckBlock(polkadot_sdk::sc_cli::CheckBlockCmd),
}

// Implementação obrigatória para o SDK reconhecer o teu nó
impl SubstrateCli for Cli {
	fn impl_name() -> String { "Moral Money Node".into() }
	fn impl_version() -> String { env!("CARGO_PKG_VERSION").into() }
	fn description() -> String { "Blockchain MMECO com Polkadot SDK 2025".into() }
	fn author() -> String { "Moral Money Team".into() }
	fn support_url() -> String { "https://github.com/nuno/mmeco/issues".into() }
	fn copyright_start_year() -> i32 { 2025 }
	fn load_spec(&self, _id: &str) -> Result<Box<dyn ChainSpec>, String> {
		// Amanhã criamos o ChainSpec real (os parâmetros da rede)
		Err("ChainSpec ainda não configurado. Passo seguinte!".into())
	}
}

fn main() -> polkadot_sdk::sc_cli::Result<()> {
	let cli = Cli::parse();

	match &cli.subcommand {
		Some(Subcommand::PurgeChain(cmd)) => {
			let runner = cli.create_runner(cmd)?;
			runner.sync_run(|config| cmd.run(config.database))
		},
		None => {
			let runner = cli.create_runner(&cli.run)?;
			println!("🚀 Moral Money Node a arrancar com Polkadot SDK...");
			// Aqui o runner iniciaria o serviço completo
			runner.run_node_until_exit(|_config| async move {
				Ok(())
			})
		},
		_ => Ok(()),
	}
}
