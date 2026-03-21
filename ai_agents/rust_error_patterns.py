"""
Rust Error Patterns - Base de conhecimento para erros Rust/Substrate
Contém padrões comuns e soluções conhecidas
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable


@dataclass
class ErrorPattern:
    """Padrão de erro com solução."""
    code: str
    category: str
    patterns: List[str]  # Palavras-chave para identificar
    explanation: str
    solution: str
    example_fix: Optional[str] = None
    substrate_related: bool = False


# Base de dados de padrões de erros Rust comuns
RUST_ERROR_PATTERNS: Dict[str, ErrorPattern] = {

    # ========== ERROS DE TIPOS ==========
    "E0277": ErrorPattern(
        code="E0277",
        category="Tipos e Traits",
        patterns=["the trait bound", "cannot be formatted", "doesn't implement", "missing"],
        explanation="O tipo não implementa o trait necessário. Frequente em derive macros do Substrate.",
        solution="Adicionar o derive correto ou implementar o trait manualmente.",
        example_fix='''
# Adicionar derive para traits comuns do Substrate:
#[derive(Encode, Decode, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]

# Para erros de Clone:
#[derive(Clone)]

# Para erros de PartialEq:
#[derive(PartialEq)
''',
        substrate_related=True
    ),
    
    "E0283": ErrorPattern(
        code="E0283",
        category="Tipos e Traits",
        patterns=["type annotations needed", "cannot infer type"],
        explanation="O compilador não consegue inferir o tipo. Frequente em retornos de funções.",
        solution="Adicionar anotação de tipo explícita.",
        example_fix='''
let value: u32 = some_function();
''',
    ),
    
    "E0308": ErrorPattern(
        code="E0308",
        category="Tipos e Traits",
        patterns=["mismatched types", "expected", "found"],
        explanation="Tipos incompatíveis. Problema comum com tipos de peso (Weight) e Balance.",
        solution="Converter explicitamente ou usar método correto (e.g., .into(), .saturated_into())",
        example_fix='''
# Para Weight:
<T as frame_system::Config>::BlockWeights::get().max_block

# Para Balance:
<T::Currency as Currency<AccountId>>::free_balance(&account)
''',
        substrate_related=True
    ),
    
    # ========== ERROS DE IMPORTS/MÓDULOS ==========
    "E0432": ErrorPattern(
        code="E0432",
        category="Imports e Módulos",
        patterns=["unresolved import", "could not be found"],
        explanation="Módulo ou import não encontrado. Verificar Cargo.toml e path.",
        solution="Verificar que o crate está em Cargo.toml e o caminho está correto.",
        example_fix='''
# Verificar em Cargo.toml:
[dependencies]
frame-support = { git = "...", tag = "..." }

# Import correto:
use frame_support::{dispatch, traits::Everything};
''',
        substrate_related=True
    ),
    
    "E0433": ErrorPattern(
        code="E0433",
        category="Imports e Módulos",
        patterns=["failed to resolve", "could not find"],
        explanation="Falha ao resolver módulo. Problema com path ou feature flags.",
        solution="Verificar feature flags habilitado ou path do módulo.",
        example_fix='''
# Em Cargo.toml:
[features]
default = ["std"]
std = [
    "frame-support/std",
    "sp-std/std",
]
''',
        substrate_related=True
    ),
    
    # ========== ERROS DE FRAME/SUBSTRATE ==========
    "MaxEncodedLen": ErrorPattern(
        code="E0277-MaxEncodedLen",
        category="Substrate Pallet",
        patterns=["MaxEncodedLen", "doesn't implement `MaxEncodedLen`"],
        explanation="O tipo não implementa MaxEncodedLen necessário para storage.",
        solution="Adicionar derive(MaxEncodedLen) ao tipo.",
        example_fix='''
#[derive(Encode, Decode, MaxEncodedLen, TypeInfo)]
pub struct MyType<T: Config> {
    pub value: u32,
}
''',
        substrate_related=True
    ),
    
    "StorageValue": ErrorPattern(
        code="StorageValue",
        category="Substrate Storage",
        patterns=["StorageValue", "trait bound", "StorageMap", "CountedStorageMap"],
        explanation="Erro com tipos de storage do Frame. Problema com generics ou tipos.",
        solution="Verificar generics corretos e implementar traits necessários.",
        example_fix='''
#[pallet::storage]
pub type MyStorage<T: Config> = StorageValue<
    _,
    u32,
    ValueQuery,
>;
''',
        substrate_related=True
    ),
    
    "pallet_decl": ErrorPattern(
        code="pallet_decl",
        category="Substrate Pallet",
        patterns=["`pallet::`", "attribute", "invalid type", "Config"],
        explanation="Erro na declaração do pallet. Config mal definido.",
        solution="Verificar que Config implementa as traits necessárias.",
        example_fix='''
#[pallet::config]
pub trait Config: frame_system::Config {
    type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
}
''',
        substrate_related=True
    ),
    
    # ========== ERROS DE SINTASE ==========
    "E0435": ErrorPattern(
        code="E0435",
        category="Sintaxe",
        patterns=["attempting to override", "method", "const", "not found"],
        explanation="Tentativa de sobrescrever método não permitido.",
        solution="Verificar assinatura correta do método a sobrescrever.",
    ),
    
    "E0769": ErrorPattern(
        code="E0769",
        category="Sintaxe",
        patterns=["field", "private", "not accessible"],
        explanation="Campo privado não acessível. Problema com encapsulamento.",
        solution="Usar método público ou getter disponível.",
    ),
    
    # ========== ERROS DE BUILD/LINKING ==========
    "linking": ErrorPattern(
        code="LINK",
        category="Build/Linking",
        patterns=["linking", "wasm", "undefined reference", "native"],
        explanation="Erro de linking. Problema comum com build WASM vs native.",
        solution="Executar `cargo clean` e reconstruir. Verificar features.",
        example_fix='''
# Limpar e reconstruir:
cargo clean
cargo build --release

# Para WASM:
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
''',
        substrate_related=True
    ),
    
    "wasm-opt": ErrorPattern(
        code="WASM-OPT",
        category="Build/Linking",
        patterns=["wasm-opt", "optimization", "failed to run"],
        explanation="Falha na otimização WASM. Problema com wasm-opt ou código incompatível.",
        solution="Verificar código Rust válido ou atualizar wasm-pack.",
        example_fix='''
# Instalar wasm-opt:
cargo install wasm-opt

# Ou build sem otimização:
cargo build --release -Z build-std=std,panic=unwind
''',
        substrate_related=True
    ),
}


# Padrões específicos do Polkadot SDK
SUBSTRATE_SPECIFIC_PATTERNS: Dict[str, str] = {
    # Storage patterns
    r"StorageValue.*ValueQuery": "Use `StorageValue<_>` with proper type",
    r"StorageMap.*Hasher": "Specify hasher (Twox64Concat, Blake2_128Concat, etc.)",
    r"CountedStorageMap": "Similar to StorageMap, track count automatically",
    
    # Pallet patterns
    r"pallet::error": "Define custom errors using #[pallet::error]",
    r"pallet::event": "Define events with #[pallet::event] and emit! macro",
    r"pallet::storage": "Define storage items with #[pallet::storage]",
    r"pallet::call": "Define dispatchable calls with #[pallet::call]",
    
    # Config patterns
    r"trait Config": "Pallet must define Config trait with frame_system::Config",
    r"type RuntimeEvent": "RuntimeEvent must be properly configured for events",
    r"type Balance": "Balance type must implement Currency trait",
    
    # Weight patterns
    r"Weight": "Use proper weight type: T::BlockWeights::get().max_block",
    r"DispatchClass": "Use DispatchClass::Normal or DispatchClass::Operational",
    
    # Origin patterns
    r"Origin": "Use EnsureOrigin, EnsureSigned, EnsureRoot for origin checks",
    r"EnsureSigned": "Verify transaction is from signed account",
    r"EnsureRoot": "Bypass checks (use carefully!)",
}


def identify_error_category(error_msg: str) -> List[str]:
    """Identifica categorias de erro baseado na mensagem."""
    categories = []
    error_lower = error_msg.lower()
    
    for pattern_obj in RUST_ERROR_PATTERNS.values():
        for keyword in pattern_obj.patterns:
            if keyword.lower() in error_lower:
                categories.append(pattern_obj.category)
                break
    
    # Verificar padrões Substrate
    for pattern, desc in SUBSTRATE_SPECIFIC_PATTERNS.items():
        import re
        if re.search(pattern, error_msg, re.IGNORECASE):
            if "Substrate" not in categories:
                categories.append("Substrate Specific")
    
    return list(set(categories))


def get_solution_for_error(error_msg: str) -> Optional[ErrorPattern]:
    """
    Procura solução para uma mensagem de erro.
    
    Args:
        error_msg: Mensagem de erro completa
        
    Returns:
        ErrorPattern com solução ou None
    """
    error_code = None
    import re
    match = re.search(r'\bE\d{4}\b', error_msg)
    if match:
        error_code = match.group(0)
    
    # Primeiro tentar por código exato
    if error_code and error_code in RUST_ERROR_PATTERNS:
        return RUST_ERROR_PATTERNS[error_code]
    
    # Procurar por padrões de texto
    error_lower = error_msg.lower()
    
    # Verificar cada padrão
    for pattern_obj in RUST_ERROR_PATTERNS.values():
        for keyword in pattern_obj.patterns:
            if keyword.lower() in error_lower:
                return pattern_obj
    
    return None


def format_solution_message(pattern: ErrorPattern, context: str = "") -> str:
    """Formata mensagem de solução completa."""
    msg = f"""
## 📋 Erro: {pattern.code} - {pattern.category}

### 🔍 Explicação
{pattern.explanation}

### ✅ Solução
{pattern.solution}
"""
    
    if pattern.substrate_related:
        msg += "\n### 🔗 Substrate/Polkadot SDK"
        msg += "\nEste é um erro comum no ecossistema Substrate."
    
    if pattern.example_fix:
        msg += f"\n### 💡 Exemplo de Correção\n```rust\n{pattern.example_fix}\n```"
    
    if context:
        msg += f"\n### 📌 Contexto\n{context}"
    
    return msg


def get_common_substrate_errors() -> List[ErrorPattern]:
    """Retorna lista de erros comuns do Substrate."""
    return [p for p in RUST_ERROR_PATTERNS.values() if p.substrate_related]


# ============================================
# PARSER PARA OUTPUT DO CARGO
# ============================================

def parse_cargo_error(output: str) -> List[Dict]:
    """
    Faz parse do output do cargo build e extrai erros.
    
    Args:
        output: Output completo do cargo build
        
    Returns:
        Lista de dicts com informações do erro
    """
    errors = []
    
    # Padrão para erro Rust: error[E0xxx]
    import re
    error_blocks = re.split(r'\n(?=error\[)', output)
    
    for block in error_blocks:
        if not block.strip():
            continue
        
        error_info = {
            'raw': block,
            'code': None,
            'message': None,
            'file': None,
            'line': None,
            'hints': []
        }
        
        # Extrair código
        code_match = re.search(r'error\[(E\d{4})\]', block)
        if code_match:
            error_info['code'] = code_match.group(1)
        
        # Extrair mensagem principal (primeira linha depois do código)
        lines = block.split('\n')
        for i, line in enumerate(lines):
            if 'error[' in line or line.startswith('error'):
                # A mensagem está na mesma linha ou próxima
                msg = line.replace(f'error[{error_info["code"]}]', '').replace('error:', '').strip()
                if msg:
                    error_info['message'] = msg
                elif i + 1 < len(lines):
                    error_info['message'] = lines[i + 1].strip()
                break
        
        # Extrair localização (--> path:line)
        location_match = re.search(r'-->\s+([^\s:]+):(\d+)', block)
        if location_match:
            error_info['file'] = location_match.group(1)
            error_info['line'] = int(location_match.group(2))
        
        # Extrair hints (sugestões do compilador)
        hint_matches = re.findall(r'help:\s*(.+)', block)
        error_info['hints'] = hint_matches
        
        if error_info['code'] or error_info['message']:
            errors.append(error_info)
    
    return errors
