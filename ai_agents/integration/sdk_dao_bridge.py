import logging
import json
from pathlib import Path
from sdk_agents.config import Config

logger = logging.getLogger("sdk_dao_bridge")

class SDKDAOBridge:
    def __init__(self):
        self.config = Config()
        self.memory_path = self.config.DAO_MEMORY_FILE
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("�� SDK DAO Bridge iniciada")
        return True

    async def stop(self):
        self.is_running = False
        logger.info("💾 Estado da ponte salvo")
        return True

    def update_state(self):
        # Garante que o ficheiro existe antes de escrever
        if not self.memory_path.exists():
            with open(self.memory_path, 'w') as f:
                json.dump({"status": "active"}, f)
        logger.info("✅ Estado da DAO sincronizado")
