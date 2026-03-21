"""
Documentation Manager - Sistema de atualização automática de documentação
Gerencia atualização de arquivos MD com base em erros detectados e aprendizados
"""

import json
import re
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

# Importar configurações
sys.path.insert(0, str(Path(__file__).parent))
from config import get_config, validate_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ErrorEntry:
    """Entrada de erro para documentação."""
    timestamp: datetime
    error_code: Optional[str]
    message: str
    file: Optional[str]
    line: Optional[int]
    solution: Optional[str]
    categories: List[str]
    confidence: float
    context: str


class DocumentationManager:
    """
    Sistema de atualização automática de documentação.
    Mantém arquivos MD sincronizados com erros detectados e soluções aprendidas.
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.error_tracker_files = self.config.get_error_files()
        
        # Contadores de atualização
        self.stats = {
            'files_updated': 0,
            'entries_added': 0,
            'solutions_added': 0,
            'categories_updated': 0
        }
    
    def update_error_tracker(self, errors: List[Dict]):
        """
        Atualiza o error-tracker com novos erros detectados.
        
        Args:
            errors: Lista de erros detectados pelo error detector
        """
        if not errors:
            return
        
        logger.info(f"📝 Atualizando error-tracker com {len(errors)} erros")
        
        # Atualizar all-errors.md
        self._update_all_errors(errors)
        
        # Atualizar frequent-errors.md (se houver erros frequentes)
        self._update_frequent_errors(errors)
        
        # Atualizar resolved.md (se houver soluções)
        self._update_resolved_errors(errors)
        
        # Atualizar lessons-learned.md
        self._update_lessons_learned(errors)
        
        # Atualizar quick-reference.md
        self._update_quick_reference(errors)
        
        logger.info(f"✅ Error-tracker atualizado: {self.stats['files_updated']} arquivos, {self.stats['entries_added']} entradas")
    
    def _update_all_errors(self, errors: List[Dict]):
        """Atualiza o arquivo all-errors.md."""
        file_path = self.error_tracker_files['all_errors']
        
        # Carregar conteúdo existente
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()
        
        # Gerar novas entradas
        new_entries = []
        for error in errors:
            entry = self._format_error_entry(error, "all_errors")
            if entry and entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            # Adicionar ao final do arquivo
            content = existing_content
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'.join(new_entries)
            file_path.write_text(content, encoding='utf-8')
            
            self.stats['files_updated'] += 1
            self.stats['entries_added'] += len(new_entries)
            logger.debug(f"📝 {len(new_entries)} novos erros adicionados ao all-errors.md")
    
    def _update_frequent_errors(self, errors: List[Dict]):
        """Atualiza o arquivo frequent-errors.md."""
        file_path = self.error_tracker_files['frequent_errors']
        
        # Contar erros por código/mensagem
        error_counts = defaultdict(int)
        for error in errors:
            key = error.get('code') or error.get('message', '')[:50]
            error_counts[key] += 1
        
        # Identificar erros frequentes (>= 3 ocorrências)
        frequent_errors = [
            (key, count) for key, count in error_counts.items() 
            if count >= 3
        ]
        
        if not frequent_errors:
            return
        
        # Carregar conteúdo existente
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()
        
        # Gerar novas entradas
        new_entries = []
        for error_key, count in frequent_errors:
            if f"## {error_key}" not in existing_content:
                entry = self._format_frequent_error_entry(error_key, count)
                new_entries.append(entry)
        
        if new_entries:
            content = existing_content
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'.join(new_entries)
            file_path.write_text(content, encoding='utf-8')
            
            self.stats['files_updated'] += 1
            self.stats['entries_added'] += len(new_entries)
            logger.debug(f"🔥 {len(new_entries)} erros frequentes adicionados ao frequent-errors.md")
    
    def _update_resolved_errors(self, errors: List[Dict]):
        """Atualiza o arquivo resolved.md."""
        resolved_errors = [
            error for error in errors 
            if error.get('solution') and error.get('confidence', 0) > 0.5
        ]
        
        if not resolved_errors:
            return
        
        file_path = self.error_tracker_files['resolved_errors']
        
        # Carregar conteúdo existente
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()
        
        # Gerar novas entradas
        new_entries = []
        for error in resolved_errors:
            entry = self._format_resolved_error_entry(error)
            if entry and entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            content = existing_content
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'.join(new_entries)
            file_path.write_text(content, encoding='utf-8')
            
            self.stats['files_updated'] += 1
            self.stats['solutions_added'] += len(new_entries)
            logger.debug(f"✅ {len(new_entries)} soluções adicionadas ao resolved.md")
    
    def _update_lessons_learned(self, errors: List[Dict]):
        """Atualiza o arquivo lessons-learned.md."""
        file_path = self.error_tracker_files['lessons_learned']
        
        # Extrair categorias e padrões
        categories = set()
        patterns = set()
        
        for error in errors:
            categories.update(error.get('categories', []))
            if error.get('solution'):
                patterns.add(self._extract_pattern_from_solution(error['solution']))
        
        if not categories and not patterns:
            return
        
        # Carregar conteúdo existente
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()
        
        # Gerar novas lições
        new_lessons = []
        
        for category in categories:
            if f"## {category}" not in existing_content:
                lesson = self._format_lesson_entry(category, "category")
                new_lessons.append(lesson)
        
        for pattern in patterns:
            if pattern and f"## {pattern}" not in existing_content:
                lesson = self._format_lesson_entry(pattern, "pattern")
                new_lessons.append(lesson)
        
        if new_lessons:
            content = existing_content
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'.join(new_lessons)
            file_path.write_text(content, encoding='utf-8')
            
            self.stats['files_updated'] += 1
            self.stats['categories_updated'] += len(new_lessons)
            logger.debug(f"📚 {len(new_lessons)} lições aprendidas adicionadas ao lessons-learned.md")
    
    def _update_quick_reference(self, errors: List[Dict]):
        """Atualiza o arquivo quick-reference.md."""
        file_path = self.error_tracker_files['quick_reference']
        
        # Extrair comandos e snippets úteis
        commands = set()
        snippets = set()
        
        for error in errors:
            if error.get('solution'):
                cmd = self._extract_command_from_solution(error['solution'])
                if cmd:
                    commands.add(cmd)
                
                snippet = self._extract_snippet_from_solution(error['solution'])
                if snippet:
                    snippets.add(snippet)
        
        if not commands and not snippets:
            return
        
        # Carregar conteúdo existente
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()
        
        # Gerar novas referências
        new_refs = []
        
        for cmd in commands:
            if cmd not in existing_content:
                ref = self._format_command_reference(cmd)
                new_refs.append(ref)
        
        for snippet in snippets:
            if snippet not in existing_content:
                ref = self._format_snippet_reference(snippet)
                new_refs.append(ref)
        
        if new_refs:
            content = existing_content
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'.join(new_refs)
            file_path.write_text(content, encoding='utf-8')
            
            self.stats['files_updated'] += 1
            logger.debug(f"💡 {len(new_refs)} referências rápidas adicionadas ao quick-reference.md")
    
    # Formatação de entradas
    
    def _format_error_entry(self, error: Dict, entry_type: str) -> Optional[str]:
        """Formata entrada de erro para arquivos MD."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        code = error.get('code', 'SEM_CÓDIGO')
        message = error.get('message', 'Mensagem desconhecida')
        file = error.get('file', 'Desconhecido')
        line = error.get('line', '?')
        categories = ', '.join(error.get('categories', ['Desconhecida']))
        confidence = error.get('confidence', 0)
        
        return f"""
## [{timestamp}] {code}

**Mensagem:** {message}

**Localização:** {file}:{line}

**Categorias:** {categories}

**Confiança:** {confidence:.0%}

**Contexto:** {error.get('context', 'Nenhum')}

---
"""
    
    def _format_frequent_error_entry(self, error_key: str, count: int) -> str:
        """Formata entrada de erro frequente."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        return f"""
## [{timestamp}] {error_key}

**Ocorrências:** {count}

**Status:** Frequente (>= 3 ocorrências)

**Ação:** Investigar causa raiz e implementar solução permanente

---
"""
    
    def _format_resolved_error_entry(self, error: Dict) -> str:
        """Formata entrada de erro resolvido."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        code = error.get('code', 'SEM_CÓDIGO')
        
        return f"""
## [{timestamp}] {code}

**Problema:** {error.get('message', 'Descrição não disponível')}

**Solução:**
{error.get('solution', 'Solução não disponível')}

**Categorias:** {', '.join(error.get('categories', []))}

**Confiança:** {error.get('confidence', 0):.0%}

---
"""
    
    def _format_lesson_entry(self, topic: str, lesson_type: str) -> str:
        """Formata entrada de lição aprendida."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        return f"""
## {topic}

**Tipo:** {lesson_type}

**Data:** {timestamp}

**Descrição:** Lição aprendida a partir de erros recorrentes

**Aplicação:** Aplicar este conhecimento em desenvolvimento futuro

---
"""
    
    def _format_command_reference(self, command: str) -> str:
        """Formata referência de comando."""
        return f"""
### {command}

```bash
{command}
```

**Uso:** Comando útil para resolução de erros

---
"""
    
    def _format_snippet_reference(self, snippet: str) -> str:
        """Formata referência de snippet."""
        return f"""
### {snippet[:50]}...

```rust
{snippet}
```

**Uso:** Snippet de código para resolução de erros

---
"""
    
    # Extração de informações
    
    def _extract_pattern_from_solution(self, solution: str) -> Optional[str]:
        """Extrai padrão de solução."""
        # Procurar por padrões comuns
        patterns = [
            r'derive\([^)]+\)',  # derive macros
            r'impl[^{{]+{{',     # implementações
            r'trait[^{{]+{{',    # traits
            r'struct[^{{]+{{',   # structs
        ]
        
        for pattern in patterns:
            match = re.search(pattern, solution, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_command_from_solution(self, solution: str) -> Optional[str]:
        """Extrai comando de solução."""
        # Procurar por comandos cargo
        cargo_commands = [
            r'cargo\s+\w+',     # cargo build, cargo check, etc.
            r'rustup\s+\w+',    # rustup update, etc.
            r'rustc\s+\w+',     # rustc flags
        ]
        
        for pattern in cargo_commands:
            match = re.search(pattern, solution, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_snippet_from_solution(self, solution: str) -> Optional[str]:
        """Extrai snippet de código de solução."""
        # Procurar por blocos de código Rust
        rust_patterns = [
            r'```rust\s*([^`]+)\s*```',  # Markdown code block
            r'```([^`]+)\s*```',         # Generic code block
            r'impl\s+[^{{]+{{[^}]+}}',   # Implementation block
        ]
        
        for pattern in rust_patterns:
            match = re.search(pattern, solution, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0)
        
        return None
    
    def generate_summary_report(self) -> Path:
        """Gera relatório resumido de documentação."""
        report_file = self.config.project_root / f"documentation-summary-{datetime.now().strftime('%Y%m%d')}.md"
        
        content = f"""# Relatório de Documentação - {datetime.now().strftime('%Y-%m-%d')}

## Estatísticas de Atualização

- **Arquivos Atualizados:** {self.stats['files_updated']}
- **Entradas Adicionadas:** {self.stats['entries_added']}
- **Soluções Documentadas:** {self.stats['solutions_added']}
- **Categorias Atualizadas:** {self.stats['categories_updated']}

## Arquivos Atualizados

"""
        
        for file_type, file_path in self.error_tracker_files.items():
            if file_path.exists():
                content += f"- **{file_type}:** {file_path.name}\n"
        
        content += f"""

## Próximas Atualizações

- Verificar erros frequentes sem solução
- Atualizar quick-reference com novos comandos
- Revisar lições aprendidas

---
*Relatório gerado automaticamente pelo Documentation Manager*
"""
        
        try:
            report_file.write_text(content, encoding='utf-8')
            logger.info(f"📊 Relatório de documentação gerado: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"💥 Erro ao gerar relatório: {e}")
            return report_file
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de atualização."""
        return self.stats.copy()
    
    def print_stats(self):
        """Imprime estatísticas de documentação."""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📚 DOCUMENTATION MANAGER STATS")
        print("="*60)
        print(f"Files Updated: {stats['files_updated']}")
        print(f"Entries Added: {stats['entries_added']}")
        print(f"Solutions Added: {stats['solutions_added']}")
        print(f"Categories Updated: {stats['categories_updated']}")
        
        print("\n📁 TRACKED FILES:")
        for file_type, file_path in self.error_tracker_files.items():
            status = "✅" if file_path.exists() else "❌"
            print(f"  {status} {file_type}: {file_path.name}")
        
        print("="*60)


def main():
    """Função principal para teste."""
    docs_manager = DocumentationManager()
    
    # Testar atualização com erros simulados
    test_errors = [
        {
            'code': 'E0277',
            'message': 'the trait bound is not satisfied',
            'file': 'src/lib.rs',
            'line': 42,
            'solution': 'Adicione #[derive(Clone)] ao tipo',
            'categories': ['Tipos e Traits'],
            'confidence': 0.8,
            'context': 'pallet_projects'
        }
    ]
    
    docs_manager.update_error_tracker(test_errors)
    docs_manager.print_stats()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())