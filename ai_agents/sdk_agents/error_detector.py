import asyncio
import logging
import re
from datetime import datetime
from sdk_agents.config import Config
from sdk_agents.documentation_manager import DocumentationManager

logger = logging.getLogger("error_detector")

class ErrorDetector:
    def __init__(self):
        self.config = Config()
        self.docs = DocumentationManager()
        self.is_running = True

    async def analyze_build(self):
        logger.info("🔨 Executando análise do motor Rust...")
        try:
            # O agente corre a verificação dele por trás dos panos
            process = await asyncio.create_subprocess_shell(
                "cd blockchain-core && cargo build --color=never",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            output = stderr.decode()
            
            if process.returncode == 0:
                return []
            
            logger.warning("❌ O motor falhou! O Agente está a ler os erros...")
            errors = []
            
            # O agente procura as linhas exatas do Rust (ex: error[E0599])
            error_pattern = re.compile(r"error\[(E\d+)\]:\s+(.+)")
            
            for line in output.split('\n'):
                match = error_pattern.search(line)
                if match:
                    errors.append({
                        'code': match.group(1),
                        'message': match.group(2).strip(),
                        'file': 'blockchain-core/runtime/src/lib.rs',
                        'category': 'Rust Traits/Syntax',
                        'confidence': 100,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            if errors:
                logger.info(f"👀 O Agente detetou {len(errors)} erros. A escrever no relatório...")
            return errors
        except Exception as e:
            logger.error(f"Erro no detetor: {e}")
            return []

    async def start(self):
        logger.info("🔍 Olhos bem abertos: Monitorizando o código...")
        while self.is_running:
            errors = await self.analyze_build()
            if errors:
                self.docs.update_error_tracker(errors)
            await asyncio.sleep(15)  # Acorda de 15 em 15 segundos

    def stop(self):
        self.is_running = False
        logger.info("🛑 Fechando os olhos do Error Detector")
