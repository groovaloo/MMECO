"""
Claude Integration Module - VERSÃO FINAL PRODUCTION-READY
Integração completamente compatível com a API real dos agentes SDK
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaudeIntegration:
    """
    Classe de integração entre Claude e o sistema de agentes SDK.
    100% compatível com MemoryManager e DocumentationManager reais.
    """
    
    def __init__(self, memory_manager, error_detector=None, doc_manager=None):
        self.memory = memory_manager
        self.detector = error_detector
        self.docs = doc_manager
        
        # Garante que o diretório de logs existe
        self.log_path = Path("logs/claude_interactions.json")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ ClaudeIntegration inicializado com sucesso")
    
    def learn_solution(self, error_msg: str, solution: str, context: str = "claude_analysis", confidence: float = 0.85) -> str:
        try:
            error_key = self.memory.learn_error(
                error_msg=error_msg,
                solution=solution,
                context=context
            )
            logger.info(f"📚 Claude ensinou solução para: {error_key}")
            self.log_interaction("learn_solution", {
                "error_key": error_key,
                "confidence": confidence,
                "context": context
            })
            return error_key
        except Exception as e:
            logger.error(f"💥 Erro ao ensinar solução: {e}")
            return ""
    
    def search_known_solution(self, error_msg: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.memory.search_solution(error_msg)
            if result:
                logger.info(f"✅ Solução encontrada (confiança: {result['confidence']:.0%})")
            else:
                logger.info(f"❌ Nenhuma solução conhecida para este erro")
            return result
        except Exception as e:
            logger.error(f"💥 Erro ao buscar solução: {e}")
            return None
    
    def get_similar_errors(self, error_msg: str, threshold: float = 0.5) -> List[Any]:
        try:
            similar = self.memory.get_similar_errors(error_msg, threshold=threshold)
            logger.info(f"🔍 Encontrados {len(similar)} erros similares")
            return similar
        except Exception as e:
            logger.error(f"💥 Erro ao buscar erros similares: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        try:
            return self.memory.get_error_stats()
        except Exception as e:
            logger.error(f"💥 Erro ao obter estatísticas: {e}")
            return {}
    
    def update_documentation(self, errors: List[Dict[str, Any]]) -> bool:
        if not self.docs:
            logger.warning("⚠️  DocumentationManager não disponível")
            return False
        try:
            self.docs.update_error_tracker(errors)
            logger.info(f"📝 Documentação atualizada com {len(errors)} erros")
            self.log_interaction("update_documentation", {
                "errors_count": len(errors),
                "files_updated": self.docs.stats.get('files_updated', 0)
            })
            return True
        except Exception as e:
            logger.error(f"💥 Erro ao atualizar documentação: {e}")
            return False
    
    def analyze_and_learn(self, error_msg: str, claude_solution: str) -> Dict[str, Any]:
        result = {
            "error_key": None,
            "learned": False,
            "documented": False,
            "similar_found": 0
        }
        try:
            # 1. Verificar se já existe solução conhecida
            existing = self.search_known_solution(error_msg)
            if existing:
                logger.info(f"ℹ️  Já existe solução conhecida (confiança: {existing['confidence']:.0%})")
                result["existing_solution"] = existing
            
            # 2. Ensinar nova solução
            error_key = self.learn_solution(
                error_msg=error_msg,
                solution=claude_solution,
                context="claude_analysis",
                confidence=0.90
            )
            result["error_key"] = error_key
            result["learned"] = bool(error_key)
            
            # 3. Atualizar documentação
            if self.docs and error_key:
                error_dict = {
                    "code": self.memory._extract_error_code(error_msg),
                    "message": error_msg,
                    "solution": claude_solution,
                    "confidence": 0.90,
                    "categories": self.memory._extract_categories(error_msg),
                    "context": "claude_analysis"
                }
                self.update_documentation([error_dict])
                result["documented"] = True
            
            # 4. Buscar erros similares para contexto
            similar = self.get_similar_errors(error_msg, threshold=0.6)
            result["similar_found"] = len(similar)
            
            logger.info(f"✅ Workflow completo: {error_key} (similares: {len(similar)})")
        except Exception as e:
            logger.error(f"💥 Erro no workflow: {e}")
        
        return result
    
    def log_interaction(self, action: str, data: Dict[str, Any]) -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        }
        try:
            logs = []
            if self.log_path.exists():
                try:
                    with open(self.log_path, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"⚠️  Log corrompido, criando novo")
                    logs = []
            
            logs.append(log_entry)
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"�� Interação registada: {action}")
        except Exception as e:
            logger.error(f"💥 Erro ao registar interação: {e}")
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        try:
            if not self.log_path.exists():
                return {"total_interactions": 0}
            
            with open(self.log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            actions = {}
            for log in logs:
                action = log.get("action", "unknown")
                actions[action] = actions.get(action, 0) + 1
            
            return {
                "total_interactions": len(logs),
                "actions_breakdown": actions,
                "last_interaction": logs[-1]["timestamp"] if logs else None
            }
        except Exception as e:
            logger.error(f"💥 Erro ao obter estatísticas: {e}")
            return {"error": str(e)}
    
    def print_status(self):
        print("\n" + "="*70)
        print("🤖 CLAUDE INTEGRATION STATUS")
        print("="*70)
        
        if self.memory:
            mem_stats = self.get_memory_stats()
            print(f"\n🧠 MEMÓRIA:")
            print(f"  Total Erros: {mem_stats.get('total_entries', 0)}")
            print(f"  Resolvidos: {mem_stats.get('resolved_entries', 0)}")
            print(f"  Pendentes: {mem_stats.get('pending_entries', 0)}")
            print(f"  Confiança Média: {mem_stats.get('average_confidence', 0):.0%}")
        
        if self.docs:
            doc_stats = self.docs.get_stats()
            print(f"\n📚 DOCUMENTAÇÃO:")
            print(f"  Ficheiros Atualizados: {doc_stats.get('files_updated', 0)}")
            print(f"  Entradas Adicionadas: {doc_stats.get('entries_added', 0)}")
            print(f"  Soluções Documentadas: {doc_stats.get('solutions_added', 0)}")
        
        int_stats = self.get_interaction_stats()
        print(f"\n🔗 INTERAÇÕES CLAUDE:")
        print(f"  Total: {int_stats.get('total_interactions', 0)}")
        if int_stats.get('actions_breakdown'):
            print(f"  Ações:")
            for action, count in sorted(int_stats['actions_breakdown'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    • {action}: {count}")
        
        print("="*70 + "\n")
