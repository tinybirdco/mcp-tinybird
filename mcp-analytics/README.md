# Tinybird MCP Analytics

This is a Tinybird project that collects and stores MCP logs and metrics.

## Quickstart

Click the button below to deploy the project to your Tinybird Workspace.

<p align="center">
  <a href="https://app.tinybird.co?starter_kit=https://github.com/tinybirdco/mcp-tinybird/mcp-analytics">
    <img width="300" src="https://img.shields.io/badge/Deploy%20to-Tinybird-25283d?style=flat&labelColor=25283d&color=27f795&logo=data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNTAwIDUwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNTAwIDQyLjhsLTE1Ni4xLTQyLjgtNTQuOSAxMjIuN3pNMzUwLjcgMzQ1LjRsLTE0Mi45LTUxLjEtODMuOSAyMDUuN3oiIGZpbGw9IiNmZmYiIG9wYWNpdHk9Ii42Ii8+PHBhdGggZD0iTTAgMjE5LjlsMzUwLjcgMTI1LjUgNTcuNS0yNjguMnoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=" />
  </a>
</p>

## Logging a MCP server using the Python SDK

Add the following to your `requirements.txt` file:

```
tinybird-python-sdk>=0.1.6
```

Configure the logging handler:

```python
import logging
from multiprocessing import Queue
from tb.logger import TinybirdLoggingQueueHandler
from dotenv import load_dotenv

load_dotenv()
TB_API_URL = os.getenv("TB_API_URL")
TB_WRITE_TOKEN = os.getenv("TB_WRITE_TOKEN")

logger = logging.getLogger('your-logger-name')
handler = TinybirdLoggingQueueHandler(Queue(-1), TB_API_URL, TB_WRITE_TOKEN, 'your-app-name', ds_name="mcp_logs_python")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

Start sending your MCP logs and errors:

```python
logger.info(f"handle_call_tool {name}", extra={**extra, "tool": name})
```

Make sure you include an extra dictionary with the `tool`, `resource`, `prompt` and `session` keys when it applies.

See logger calls [here](https://github.com/tinybirdco/mcp-tinybird/blob/main/src/mcp_tinybird/server.py)


## Logging a MCP server using the TypeScript SDK

TODO

## Exploring and visualizing logs and metrics

TODO