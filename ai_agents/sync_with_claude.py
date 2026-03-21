#!/usr/bin/env python3
"""
Script de sincronização Claude ↔ Sistema de Agentes
"""

import sys
from pathlib import Path

# Adicionar paths - VERSÃO CORRIGIDA
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir / 'sdk_agents'))
sys.path.insert(0, str(current_dir / 'integration'))

# Debug inicial
print(f"🔍 Diretório atual: {current_dir}")
print(f"🔍 Procurando módulos em:")
print(f"   • {current_dir / 'sdk_agents'}")
print(f"   • {current_dir / 'integration'}")
print()

try:
    from memory_manager import MemoryManager
    from documentation_manager import DocumentationManager
    from claude_integration import ClaudeIntegration
    print("✅ Módulos importados com sucesso!\n")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("\n📁 Estrutura esperada:")
    print("ai_agents/")
    print("├── sdk_agents/")
    print("│   ├── memory_manager.py")
    print("│   └── documentation_manager.py")
    print("├── claude-integration.py")
    print("└── sync_with_claude.py")
    sys.exit(1)


def teach_current_error():
    """Ensina a solução dos erros atuais ao sistema."""
    print("🚀 Ensinando soluções dos erros atuais...\n")
    
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
    
    print(f"\n✅ Erro 1: {result1.get('error_key')}")
    print(f"✅ Erro 2: {result2.get('error_key')}")
    
    claude.print_status()
    return 0

def check_memory():
    """Verifica o que já está na memória."""
    print("🔍 Verificando memória do sistema...\n")
    
    memory = MemoryManager()
    claude = ClaudeIntegration(memory)
    
    # Mostrar status
    claude.print_status()
    
    return 0


def search_solution(error_text: str):
    """Busca solução para um erro."""
    print(f"🔍 Buscando solução para: {error_text[:50]}...\n")
    
    memory = MemoryManager()
    claude = ClaudeIntegration(memory)
    
    # Buscar solução
    result = claude.search_known_solution(error_text)
    
    if result:
        print("✅ SOLUÇÃO ENCONTRADA:")
        print(f"  Confiança: {result['confidence']:.0%}")
        print(f"  Contexto: {result['context']}")
        print(f"  Ocorrências: {result['count']}")
        print(f"\n📝 SOLUÇÃO:")
        print(result['solution'])
    else:
        print("❌ Nenhuma solução conhecida")
        print("💡 Precisa análise do Claude!")
    
    return 0


def main():
    """Menu principal."""
    import sys
    
    if len(sys.argv) < 2:
        print("USO:")
        print("  python sync_with_claude.py teach    # Ensina erro atual")
        print("  python sync_with_claude.py check    # Verifica memória")
        print("  python sync_with_claude.py search 'texto do erro'")
        return 1
    
    command = sys.argv[1]
    
    if command == "teach":
        return teach_current_error()
    elif command == "check":
        return check_memory()
    elif command == "search" and len(sys.argv) > 2:
        return search_solution(' '.join(sys.argv[2:]))
    else:
        print("❌ Comando inválido")
        return 1


if __name__ == "__main__":
    sys.exit(main())