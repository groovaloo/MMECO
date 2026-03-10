use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about = "Moral Money Node", long_about = None)]
struct Cli {
    #[arg(short, long, default_value = "moral-money-node")]
    name: String,
}

fn main() {
    let cli = Cli::parse();

    println!("--- Moral Money Ecosystem ---");
    println!("Nó inicializado com o nome: {}", cli.name);
    println!("Runtime carregado com sucesso.");
    println!("Categorias de Reputação: Construção, Agricultura, Energia, Governação, Saúde, Logística.");
    println!("Buildcoin Network: Ativa e Sincronizada");
    println!("-----------------------------");

    println!("O nó está pronto para ser integrado com o Consensus Engine.");
}
