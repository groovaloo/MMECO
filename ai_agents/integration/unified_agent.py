import asyncio
import logging
from ai_agents.sdk_agents.config import Config
from ai_agents.sdk_agents.memory_manager import MemoryManager
from ai_agents.sdk_agents.alert_system import AlertSystem
from ai_agents.sdk_agents.documentation_manager import DocumentationManager
from ai_agents.sdk_agents.error_detector import ErrorDetector
from ai_agents.integration.sdk_dao_bridge import SDKDAOBridge

logger = logging.getLogger("unified_agent")

class UnifiedAgent:
    def __init__(self):
        self.config = Config()
        self.memory_manager = MemoryManager()
        self.alert_system = AlertSystem()
        self.docs_manager = DocumentationManager()
        self.error_detector = ErrorDetector()
        self.dao_bridge = SDKDAOBridge()
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("🚀 Iniciando Unified Agent e componentes...")
        # Iniciar a ponte e o detetor
        await self.dao_bridge.start()
        asyncio.create_task(self.error_detector.start())
        return True

    async def stop(self):
        self.is_running = False
        logger.info("🛑 Parando Unified Agent...")
        await self.dao_bridge.stop()
        self.error_detector.stop()
