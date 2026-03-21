import re

# Ler ficheiro
with open('sync_with_claude.py', 'r') as f:
    lines = f.readlines()

# Encontrar onde começa a função teach_current_error
start = None
end = None
for i, line in enumerate(lines):
    if 'def teach_current_error():' in line:
        start = i
    if start is not None and i > start and line.startswith('def '):
        end = i
        break

if start is None:
    print("❌ Não encontrei a função teach_current_error")
    exit(1)

# Se não achou próxima função, vai até o fim do bloco
if end is None:
    for i in range(start+1, len(lines)):
        if lines[i].startswith('def ') or (i < len(lines)-1 and lines[i].strip() == '' and lines[i+1].startswith('def ')):
            end = i
            break

print(f"✅ Encontrei função nas linhas {start+1} a {end}")

# Nova função
new_function = '''def teach_current_error():
    """Ensina a solução dos erros atuais ao sistema."""
    print("🚀 Ensinando soluções dos erros atuais...\\n")
    
    memory = MemoryManager()
    docs = DocumentationManager()
    claude = ClaudeIntegration(memory, doc_manager=docs)
    
    # ERRO 1: MaxFreezes
    error1 = "error[E0107]: missing generics for struct ConstU32"
    sol1 = "type MaxFreezes = ConstU32<50>; // Era: ConstU32;"
    result1 = claude.analyze_and_learn(error1, sol1)
    
    # ERRO 2: UncheckedExtrinsic
    error2 = "UncheckedExtrinsic<u32> should be UncheckedExtrinsic<AccountId>"
    sol2 = "pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<AccountId, RuntimeCall, Signature, SignedExtra>;"
    result2 = claude.analyze_and_learn(error2, sol2)
    
    print(f"\\n✅ Erro 1: {result1.get('error_key')}")
    print(f"✅ Erro 2: {result2.get('error_key')}")
    
    claude.print_status()
    return 0

'''

# Substituir
lines = lines[:start] + [new_function] + lines[end:]

# Salvar
with open('sync_with_claude.py', 'w') as f:
    f.writelines(lines)

print("✅ Ficheiro atualizado!")
