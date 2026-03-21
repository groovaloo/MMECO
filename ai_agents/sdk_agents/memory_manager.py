"""
Memory Manager - Sistema unificado de memória para erros de compilação
Gerencia memória local, integração com error-tracker e aprendizado contínuo
"""

import json
import re
import hashlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

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
class MemoryEntry:
    """Entrada na memória de erros."""
    error_key: str
    error_code: Optional[str]
    original_message: str
    solution: str
    context: str
    count: int
    first_seen: datetime
    last_seen: datetime
    resolved: bool
    confidence: float
    categories: List[str]
    related_errors: List[str]
    last_updated: datetime


class MemoryManager:
    """
    Sistema unificado de memória para erros de compilação.
    Combina memória local com integração ao error-tracker.
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.memory_db: Dict[str, MemoryEntry] = {}
        self.error_tracker_files = self.config.get_error_files()
        self.memory_file = self.config.get_memory_config()['file']
        
        # Estatísticas (ANTES de load_memory!)
        self.stats = {
            'total_entries': 0,
            'resolved_entries': 0,
            'pending_entries': 0,
            'total_learned': 0,
            'total_updated': 0
        }
        
        # Carregar memória existente
        self.load_memory()
    
    def load_memory(self):
        """Carrega memória de erros do ficheiro JSON."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Converter de volta para objetos MemoryEntry
                for key, entry_data in data.items():
                    entry_data['first_seen'] = datetime.fromisoformat(entry_data['first_seen'])
                    entry_data['last_seen'] = datetime.fromisoformat(entry_data['last_seen'])
                    entry_data['last_updated'] = datetime.fromisoformat(entry_data['last_updated'])
                    self.memory_db[key] = MemoryEntry(**entry_data)
                
                self._update_stats()
                logger.info(f"✅ Memória carregada: {len(self.memory_db)} entradas")
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"⚠️  Erro ao carregar memória: {e}")
                self.memory_db = {}
        else:
            logger.info("📝 Memória vazia, criando nova")
    
    def save_memory(self):
        """Guarda memória de erros no ficheiro JSON."""
        try:
            # Converter objetos para dicionários
            data = {}
            for key, entry in self.memory_db.items():
                data[key] = asdict(entry)
                # Converter datetime para string
                data[key]['first_seen'] = entry.first_seen.isoformat()
                data[key]['last_seen'] = entry.last_seen.isoformat()
                data[key]['last_updated'] = entry.last_updated.isoformat()
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Memória salva: {len(self.memory_db)} entradas")
            
        except Exception as e:
            logger.error(f"💥 Erro ao salvar memória: {e}")
    
    def _get_error_key(self, error_msg: str, error_code: Optional[str] = None) -> str:
        """Gera chave única para erro."""
        if error_code:
            return error_code
        
        # Hash da mensagem para erros sem código
        key_data = error_msg[:200]  # Limitar para hash consistente
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _extract_error_code(self, error_msg: str) -> Optional[str]:
        """Extrai código de erro Rust (E0xxx)."""
        match = re.search(r'\bE\d{4}\b', error_msg)
        return match.group(0) if match else None
    
    def _extract_categories(self, error_msg: str) -> List[str]:
        """Extrai categorias do erro."""
        # Importar do módulo legado
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from rust_error_patterns import identify_error_category
        return identify_error_category(error_msg)
    
    def learn_error(self, error_msg: str, solution: str, context: str = "") -> str:
        """
        Aprende um novo erro ou atualiza existente.
        
        Returns:
            str: Chave do erro aprendido
        """
        error_code = self._extract_error_code(error_msg)
        error_key = self._get_error_key(error_msg, error_code)
        categories = self._extract_categories(error_msg)
        
        now = datetime.now()
        
        if error_key in self.memory_db:
            # Atualizar entrada existente
            entry = self.memory_db[error_key]
            entry.count += 1
            entry.last_seen = now
            entry.last_updated = now
            
            # Atualizar solução se for melhor
            if solution and (not entry.solution or len(solution) > len(entry.solution)):
                entry.solution = solution
                entry.resolved = True
                self.stats['total_updated'] += 1
            
            # Atualizar categorias
            entry.categories = list(set(entry.categories + categories))
            
            logger.debug(f"🔄 Atualizado erro: {error_key} (x{entry.count})")
            
        else:
            # Nova entrada
            entry = MemoryEntry(
                error_key=error_key,
                error_code=error_code,
                original_message=error_msg[:500],
                solution=solution,
                context=context,
                count=1,
                first_seen=now,
                last_seen=now,
                resolved=bool(solution),
                confidence=0.8 if solution else 0.3,
                categories=categories,
                related_errors=[],
                last_updated=now
            )
            
            self.memory_db[error_key] = entry
            self.stats['total_learned'] += 1
            logger.debug(f"📚 Novo erro aprendido: {error_key}")
        
        # Salvar memória
        self.save_memory()
        self._update_stats()
        
        return error_key
    
    def search_solution(self, error_msg: str) -> Optional[Dict]:
        """
        Procura solução para um erro.
        
        Returns:
            Dict com 'solution', 'context', 'confidence', 'count' ou None
        """
        error_code = self._extract_error_code(error_msg)
        
        # Primeiro tentar por código exato
        if error_code and error_code in self.memory_db:
            entry = self.memory_db[error_code]
            return {
                'solution': entry.solution,
                'context': entry.context,
                'confidence': 0.95 if entry.resolved else 0.5,
                'count': entry.count,
                'categories': entry.categories
            }
        
        # Procurar por similaridade
        error_lower = error_msg.lower()
        best_match = None
        best_score = 0
        
        for key, entry in self.memory_db.items():
            original = entry.original_message.lower()
            # Calcular score de similaridade
            common_words = set(error_lower.split()) & set(original.split())
            score = len(common_words) / max(len(error_lower.split()), 1)
            
            if score > best_score and score > 0.3:
                best_score = score
                best_match = entry
        
        if best_match:
            return {
                'solution': best_match.solution,
                'context': best_match.context,
                'confidence': best_score * 0.8,
                'count': best_match.count,
                'categories': best_match.categories
            }
        
        return None
    
    def get_error_stats(self) -> Dict:
        """Retorna estatísticas detalhadas dos erros."""
        self._update_stats()
        
        # Top erros mais frequentes
        top_errors = sorted(
            self.memory_db.items(),
            key=lambda x: x[1].count,
            reverse=True
        )[:10]
        
        # Distribuição por categoria
        category_dist = defaultdict(int)
        for entry in self.memory_db.values():
            for cat in entry.categories:
                category_dist[cat] += 1
        
        # Erros recentes (últimas 24h)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_errors = [
            entry for entry in self.memory_db.values()
            if entry.last_seen > recent_cutoff
        ]
        
        return {
            **self.stats,
            'top_errors': [
                {
                    'key': key,
                    'code': entry.error_code,
                    'count': entry.count,
                    'resolved': entry.resolved,
                    'categories': entry.categories
                }
                for key, entry in top_errors
            ],
            'category_distribution': dict(category_dist),
            'recent_errors_count': len(recent_errors),
            'average_confidence': self._calculate_avg_confidence(),
            'memory_size_mb': self._get_memory_size()
        }
    
    def _calculate_avg_confidence(self) -> float:
        """Calcula confiança média dos erros."""
        if not self.memory_db:
            return 0.0
        
        total_confidence = sum(entry.confidence for entry in self.memory_db.values())
        return total_confidence / len(self.memory_db)
    
    def _get_memory_size(self) -> float:
        """Retorna tamanho da memória em MB."""
        try:
            return self.memory_file.stat().st_size / (1024 * 1024)
        except FileNotFoundError:
            return 0.0
    
    def _update_stats(self):
        """Atualiza estatísticas internas."""
        self.stats['total_entries'] = len(self.memory_db)
        self.stats['resolved_entries'] = sum(1 for e in self.memory_db.values() if e.resolved)
        self.stats['pending_entries'] = self.stats['total_entries'] - self.stats['resolved_entries']
    
    def import_from_tracker(self) -> int:
        """Importa erros do error-tracker existente."""
        resolved_file = self.error_tracker_files['resolved_errors']
        if not resolved_file.exists():
            logger.warning("⚠️  Arquivo resolved.md não encontrado")
            return 0
        
        try:
            content = resolved_file.read_text()
            count = 0
            
            # Parse erros resolvidos do markdown
            import re
            pattern = r'##\s+\[.*?\]\s+.*?(?=##|\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                lines = match.strip().split('\n')
                if len(lines) > 4:
                    # Extrair código E0xxx
                    error_match = re.search(r'\bE\d{4}\b', match)
                    if error_match:
                        code = error_match.group(0)
                        solution_lines = [l for l in lines if l.strip() and not l.startswith('#')]
                        solution = '\n'.join(solution_lines)
                        
                        if code not in self.memory_db:
                            self.learn_error(
                                error_msg=match[:200],
                                solution=solution,
                                context='imported_from_tracker'
                            )
                            count += 1
            
            logger.info(f"📥 Importados {count} erros do error-tracker")
            return count
            
        except Exception as e:
            logger.error(f"💥 Erro ao importar do tracker: {e}")
            return 0
    
    def export_to_tracker(self) -> int:
        """Exporta erros resolvidos para o error-tracker."""
        resolved_file = self.error_tracker_files['resolved_errors']
        
        try:
            # Agrupar erros por código
            resolved_errors = [
                entry for entry in self.memory_db.values()
                if entry.resolved and entry.count >= 3
            ]
            
            if not resolved_errors:
                logger.info("📝 Nenhum erro resolvido para exportar")
                return 0
            
            # Gerar conteúdo markdown
            content = "# Erros Resolvidos - Exportação Automática\n\n"
            content += f"*Exportado em: {datetime.now().isoformat()}*\n\n"
            
            for entry in sorted(resolved_errors, key=lambda x: x.count, reverse=True):
                content += f"## [{entry.last_seen.strftime('%Y-%m-%d')}] {entry.error_code or entry.error_key}\n\n"
                content += f"**Ocorrências:** {entry.count}\n\n"
                content += f"**Mensagem:** {entry.original_message}\n\n"
                content += f"**Contexto:** {entry.context}\n\n"
                content += "### Solução\n\n"
                content += f"{entry.solution}\n\n"
                content += "---\n\n"
            
            # Adicionar ao arquivo existente
            if resolved_file.exists():
                existing_content = resolved_file.read_text()
                content = existing_content + "\n\n" + content
            
            resolved_file.write_text(content, encoding='utf-8')
            logger.info(f"📤 Exportados {len(resolved_errors)} erros para o tracker")
            return len(resolved_errors)
            
        except Exception as e:
            logger.error(f"💥 Erro ao exportar para tracker: {e}")
            return 0
    
    def cleanup_old_entries(self, days: int = 90) -> int:
        """Remove entradas antigas da memória."""
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        
        keys_to_remove = []
        for key, entry in self.memory_db.items():
            if entry.last_seen < cutoff and entry.count < 5:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_db[key]
            removed += 1
        
        if removed > 0:
            self.save_memory()
            self._update_stats()
            logger.info(f"🧹 Removidas {removed} entradas antigas")
        
        return removed
    
    def get_similar_errors(self, error_msg: str, threshold: float = 0.5) -> List[MemoryEntry]:
        """Retorna erros similares ao dado."""
        similar = []
        error_lower = error_msg.lower()
        
        for entry in self.memory_db.values():
            original = entry.original_message.lower()
            common_words = set(error_lower.split()) & set(original.split())
            score = len(common_words) / max(len(error_lower.split()), 1)
            
            if score >= threshold:
                similar.append(entry)
        
        return sorted(similar, key=lambda x: x.count, reverse=True)
    
    def print_status(self):
        """Imprime status da memória."""
        stats = self.get_error_stats()
        
        print("\n" + "="*60)
        print("🧠 MEMORY MANAGER STATUS")
        print("="*60)
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Resolved: {stats['resolved_entries']}")
        print(f"Pending: {stats['pending_entries']}")
        print(f"Learned: {stats['total_learned']}")
        print(f"Updated: {stats['total_updated']}")
        print(f"Memory Size: {stats['memory_size_mb']:.2f} MB")
        print(f"Avg Confidence: {stats['average_confidence']:.2f}")
        
        if stats['top_errors']:
            print("\n🔥 TOP 5 ERROS:")
            for i, error in enumerate(stats['top_errors'][:5], 1):
                status = "✅" if error['resolved'] else "❌"
                print(f"  {i}. {error['code'] or error['key']} ({error['count']}x) {status}")
        
        if stats['category_distribution']:
            print("\n📊 CATEGORIAS:")
            for cat, count in sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {cat}: {count}")
        
        print("="*60)


def main():
    """Função principal para teste."""
    manager = MemoryManager()
    
    # Testar aprendizado
    manager.learn_error(
        "error[E0277]: the trait bound `T: Clone` is not satisfied",
        "Adicione #[derive(Clone)] ao tipo",
        "pallet_projects"
    )
    
    # Testar busca
    result = manager.search_solution("error[E0277]: the trait bound")
    print(f"Busca: {result}")
    
    # Imprimir status
    manager.print_status()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())