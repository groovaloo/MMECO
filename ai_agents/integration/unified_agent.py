import asyncio
import logging
from sdk_agents.config import Config
from sdk_agents.memory_manager import MemoryManager
from sdk_agents.alert_system import AlertSystem
from sdk_agents.documentation_manager import DocumentationManager
from sdk_agents.error_detector import ErrorDetector
from integration.sdk_dao_bridge import SDKDAOBridge

logger = logging.getLogger("unified_agent")

class UnifiedAgent:
    def __init__(self):
        self.config = Config()
        self.memory_manager = MemoryManager()
        self.alert_system = AlertSystem()
        self.docs_manager = DocumentationManager()
        self.error_detector = ErrorDetector(self.memory_manager, Config)
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

if __name__ == "__main__":
    import asyncio
    import signal

    async def run_main():
        # Inicializa o Maestro
        agent = UnifiedAgent()
        
        # Define como parar graciosamente (Ctrl+C)
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(agent.stop()))

        # Arranca os motores
        success = await agent.start()
        if success:
            logger.info("✅ Sistema MMECO SDK está ON e a vigiar a Blockchain!")
            # Mantém o programa vivo enquanto o agente trabalha
            while agent.is_running:
                await asyncio.sleep(1)

    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        pass
