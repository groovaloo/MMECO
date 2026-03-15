//! Moral Money Blockchain Node - Real Substrate Core
//! Reconstruído para estabilidade tecnológica.

mod chain_spec;
mod rpc;
mod service;

use sc_cli::SubstrateCli;

fn main() -> sc_cli::Result<()> {
    // Este é o verdadeiro ponto de entrada do Substrate
    let cli = Cli::from_args();

    match &cli.subcommand {
        Some(subcommand) => {
            let runner = cli.create_runner(subcommand)?;
            runner.run_node_until_exit(|config| async move {
                service::new_full(config).map_err(sc_cli::Error::Service)
            })
        }
        None => {
            let runner = cli.create_runner(&cli.run)?;
            runner.run_node_until_exit(|config| async move {
                service::new_full(config).map_err(sc_cli::Error::Service)
            })
        }
    }
}

// Estrutura CLI real do Substrate
#[derive(Debug, clap::Parser)]
pub struct Cli {
    #[clap(flatten)]
    pub run: sc_cli::RunCmd,
    #[clap(subcommand)]
    pub subcommand: Option<Subcommands>,
}

#[derive(Debug, clap::Subcommand)]
pub enum Subcommands {
    /// Key management subcommand
    Key(sc_cli::KeySubcommand),
    /// Build a spec.
    BuildSpec(sc_cli::BuildSpecCmd),
    /// Export blocks.
    ExportBlocks(sc_cli::ExportBlocksCmd),
    /// Import blocks.
    ImportBlocks(sc_cli::ImportBlocksCmd),
    /// Check block.
    CheckBlock(sc_cli::CheckBlockCmd),
    /// Revert the chain.
    Revert(sc_cli::RevertCmd),
    /// Purge the client storage.
    PurgeChain(sc_cli::PurgeChainCmd),
    /// Export the state.
    ExportState(sc_cli::ExportStateCmd),
}

impl SubstrateCli for Cli {
    fn impl_name() -> String { "Moral Money Node".into() }
    fn impl_version() -> String { env!("CARGO_PKG_VERSION").into() }
    fn description() -> String { "Blockchain real para o ecossistema Moral Money".into() }
    fn author() -> String { "Moral Money Community".into() }
    fn support_url() -> String { "https://moralmoney.world".into() }
    fn copyright_start_year() -> i32 { 2024 }
    fn load_spec(&self, id: &str) -> std::result::Result<Box<dyn sc_service::ChainSpec>, String> {
        Ok(Box::new(chain_spec::development_config()?))
    }
}
