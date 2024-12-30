import logging
import mcp.server.stdio

logger = logging.getLogger(__name__)

class STDIOHandler:
    def __init__(self, server, init_options):
        self.server = server
        self.init_options = init_options

    async def handle_stdio(self):
        """Handle STDIO communication"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.init_options
            )
