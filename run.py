import uvicorn
from mcp_tinybird.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001, log_level="debug") 