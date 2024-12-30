import asyncio
import logging
from .stdio import STDIOHandler
from .server import create_server

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Starting MCP Tinybird STDIO server")
    server, init_options, _, _ = create_server()
    stdio_handler = STDIOHandler(server, init_options)
    asyncio.run(stdio_handler.handle_stdio())

if __name__ == "__main__":
    main() 