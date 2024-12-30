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
        default_response = Response(status_code=202)

        # Create a wrapper for send that will prevent double-sending
        sent = False
        async def wrapped_send(message):
            nonlocal sent
            if not sent:
                try:
                    await request._send(message)
                    sent = True
                except Exception as e:
                    logger.debug(f"Error in wrapped_send (might be normal): {e}")
                    # Don't re-raise - this might be expected if the client disconnected

        try:
            # Handle the message
            await self.sse.handle_post_message(
                request.scope,
                request.receive,
                wrapped_send
            )

            # Always return our response - if handle_post_message sent one,
            # our wrapped_send will prevent double-sending
            return default_response

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            if not sent:
                return Response({"error": str(e)}, status_code=500)
            # If we already sent an error response, return our default to prevent None
            return default_response

    def get_routes(self):
        return [
            Route("/sse", endpoint=self.handle_sse),
            Route("/messages", endpoint=self.handle_messages, methods=["POST"])
        ]
