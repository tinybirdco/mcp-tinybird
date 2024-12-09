# Tinybird MCP Analytics

This is a Tinybird project that collects and stores MCP logs and metrics.

## 1. Create a new Tinybird Workspace

Click the button below to deploy the project to your Tinybird Workspace.

<p align="center">
  <a href="https://app.tinybird.co?starter_kit=https://github.com/tinybirdco/mcp-tinybird/mcp-server-analytics/tinybird">
    <img width="300" src="https://img.shields.io/badge/Deploy%20to-Tinybird-25283d?style=flat&labelColor=25283d&color=27f795&logo=data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNTAwIDUwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNTAwIDQyLjhsLTE1Ni4xLTQyLjgtNTQuOSAxMjIuN3pNMzUwLjcgMzQ1LjRsLTE0Mi45LTUxLjEtODMuOSAyMDUuN3oiIGZpbGw9IiNmZmYiIG9wYWNpdHk9Ii42Ii8+PHBhdGggZD0iTTAgMjE5LjlsMzUwLjcgMTI1LjUgNTcuNS0yNjguMnoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=" />
  </a>
</p>

## 2. Send log events 

### Using Python

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

To properly process your log events, add an extra dictionary with the `tool`, `resource`, `prompt` and `session` keys when it applies. That way the provided Tinybird Workspace will be able to process metrics by tool, resource, prompt and session.

```python
logger.info(f"handle_call_tool {name}", extra={"session": session, "tool": name})
```

See some sample logger calls [here](https://github.com/tinybirdco/mcp-tinybird/blob/main/src/mcp_tinybird/server.py)

### Using TypeScript

```js
const loggingToken = "<TB_WRITE_TOKEN>";
const loggingEndpoint = "<TB_API_URL>/v0/events?name=mcp_logs";
const loggingSession = crypto.randomUUID();

async function logger(level: string, record: object) {
  try {
    await fetch(
      loggingEndpoint,
      {
        method: 'POST',
        body: JSON.stringify({
          timestamp: new Date().toISOString(),
          session: loggingSession,
          level: level,
          record: JSON.stringify(record)
        }),
        headers: { Authorization: `Bearer ${loggingToken}` }
      }
    )
      .then((res: Response) => { /**process.stderr.write("logged");**/ });
  } catch (error) {
    // process.stderr.write("error logging");
  }
```

To properly process your log events, add `tool`, `resource`, `prompt` and `session` keys in the `record` JSON object. That way the provided Tinybird Workspace will be able to process metrics by tool, resource, prompt and session.

See some sample logger calls [here](See [ClaudeKeep](https://github.com/sdairs/claudekeep/blob/main/apps/mcp/src/index.ts)

### Your Tinybird credentials

Your `TB_WRITE_TOKEN` can be found in the [Tinybird dashboard](https://app.tinybird.co/tokens) with the name `mcp_public_write_token`.

Your `TB_API_URL` is the URL of your Tinybird region.

![](./region.png)


## 3. Monitor with Grafana and Prometheus

Add this to your `prometheus.yml` file:

```yaml
scrape_configs:
  - job_name: mcp_server
    scrape_interval: 15s  # Adjust the scrape interval as needed
    scheme: 'https'
    static_configs:
      - targets: 
        - 'api.tinybird.co'  # Adjust this for your region if necessary
    metrics_path: '/v0/pipes/api_prometheus.prometheus'
    bearer_token: '<your-public-prometheus-token>'
```

Find `<your-public-prometheus-token>` in the [Tinybird dashboard](https://app.tinybird.co/tokens) with the name `prometheus`.

You should start seeing your metrics in Grafana to build your own dashboards and alerts.

![](./prometheus.png)

A sample dashboard for Grafana can be found [here](./mcp-metrics.json)

![](./dashboard.png)
