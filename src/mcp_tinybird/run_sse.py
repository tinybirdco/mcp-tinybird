import uvicorn
from starlette.applications import Starlette
from .sse import SSEHandler
from .server import create_server
import logging

logger = logging.getLogger(__name__)

def create_app():
    server, init_options, _, _ = create_server()
    sse_handler = SSEHandler(server, init_options)
    app = Starlette(routes=sse_handler.get_routes())
    return app

def main():
    app = create_app()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=3001,
        log_level="debug",
        log_config=None
    )
    
    server = uvicorn.Server(config)
    try:
        server.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 