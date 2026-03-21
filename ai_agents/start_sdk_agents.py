import asyncio
import logging
import signal
import sys
from ai_agents.integration.unified_agent import UnifiedAgent

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    print("\n" + "═"*62)
    print("║                   MMECO SDK AGENTS                           ║")
    print("║              Sistema de Gestão de Erros                      ║")
    print("═"*62 + "\n")

    agent = UnifiedAgent()
    
    # Lidar com o fecho do programa (Ctrl+C)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(agent.stop()))

    try:
        logger.info("🚀 Iniciando MMECO SDK Agents...")
        success = await agent.start()
        if success:
            # Manter o programa a correr
            while agent.is_running:
                await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"💥 Erro fatal no sistema: {e}")
    finally:
        await agent.stop()
        logger.info("🛑 Sistema encerrado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
