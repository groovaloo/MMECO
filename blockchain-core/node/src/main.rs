use std::fs::File;
use std::io::Write;

fn main() {
    println!("--- MORAL MONEY: GERADOR DE EMERGÊNCIA ---");
    
    let tesouro = 237000.0;
    let casas = 3;
    
    let report = format!(
        "# 📜 RELATÓRIO DE IMPACTO - MORAL MONEY\n\n\
        ## 🏦 ESTADO FINANCEIRO\n\
        - **Tesouro Comunitário:** {:.2} BLD\n\n\
        ## 🏗️ PRODUÇÃO\n\
        - **Casas Construídas:** {}\n\
        - **Património:** Máquina LSF + 1 Casa Comunitária (Silver Coast)\n\n\
        ## 🚀 PRÓXIMO PASSO\n\
        - Aquisição da Máquina Inglesa (Faltam 63k BLD)\n\n\
        *Documento gerado para a reunião com Steven e Investidores.*",
        tesouro, casas
    );

    let mut f = File::create("RELATORIO_COMUNIDADE.md").expect("Erro ao criar ficheiro");
    f.write_all(report.as_bytes()).expect("Erro ao escrever");

    println!("✅ SUCESSO: O ficheiro 'RELATORIO_COMUNIDADE.md' foi criado!");
    println!("👉 Podes fechar este programa e fazer: cat RELATORIO_COMUNIDADE.md");
}
