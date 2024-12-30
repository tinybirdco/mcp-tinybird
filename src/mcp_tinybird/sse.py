from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import logging

logger = logging.getLogger(__name__)

class SSEHandler:
    def __init__(self, server, init_options):
        self.server = server
        self.init_options = init_options
        self.sse = SseServerTransport("/messages")

    async def handle_sse(self, request):
        async with self.sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await self.server.run(
                streams[0], streams[1], 
                self.init_options
            )

    async def handle_messages(self, request):
        # Track ASGI message state
        response_started = False
        
        async def wrapped_send(message):
            nonlocal response_started
            message_type = message["type"]
            
            if message_type == "http.response.start":
                if response_started:
                    return
                response_started = True
                
            await request._send(message)
        
        try:
            await self.sse.handle_post_message(
                request.scope,
                request.receive,
                wrapped_send
            )
            
            if not response_started:
                response = Response(status_code=202)
                await response(request.scope, request.receive, request._send)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            if not response_started:
                response = Response({"error": str(e)}, status_code=500)
                await response(request.scope, request.receive, request._send)

    def get_routes(self):
        return [
            Route("/sse", endpoint=self.handle_sse),
            Route("/messages", endpoint=self.handle_messages, methods=["POST"])
        ]
