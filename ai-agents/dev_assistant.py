def handle_system_error(error):
    # Se o erro for de compilação Rust, o ErrorAgent deve sugerir:
    # 1. rustup update
    # 2. cargo clean
    # 3. check wasm32 target
    print(f"🚨 Agente de Erro Ativado: Analisando {error}")
    
    if "wasm32" in str(error).lower():
        return "Dica: Executa 'make init' para instalar o target WebAssembly."
    
    if "out of memory" in str(error).lower():
        return "Dica: Reduz o número de threads com 'cargo build -j 1'."

    return error_agent.handle_error(str(error))

def log_solution(problem, solution):
    # Isto cria uma base de conhecimento para o teu ecossistema MMECO
    from dev_memory import DevMemory
    memory = DevMemory()
    print(f"🧠 A guardar aprendizagem: {problem[:50]}...")
    memory.log_problem(problem, solution)
