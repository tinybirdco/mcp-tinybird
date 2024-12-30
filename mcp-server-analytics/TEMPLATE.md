The MCP Server Analytics template uses Python and Typescript logging handlers to send events to the Tinybird [Events API](https://www.tinybird.co/docs/ingest/events-api), which transforms the events and publishes metrics as Prometheus endpoints that you can integrate with your preferred observability tool.

## Set up the project

Fork the GitHub repository and deploy the data project to Tinybird.

## Send log events 

### Using Python

Add the following dependency to your `requirements.txt` file:

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

- Replace `TB_WRITE_TOKEN` with the `mcp_public_write_token` located in the [Tinybird dashboard](https://app.tinybird.co/tokens).
- Your `TB_API_URL` is the URL of your Tinybird region. See [Regions and endpoints](https://www.tinybird.co/docs/api-reference#regions-and-endpoints).

To properly process your log events, add an extra dictionary with the `tool`, `resource`, `prompt`, `mcp_server_version` and `session` keys when it applies. That way the provided Tinybird Workspace will be able to process metrics by tool, resource, prompt and session.

```python
logger.info(f"handle_call_tool {name}", extra={"session": session, "tool": name, "mcp_server_version": "0.1.4"})
```

#### Using TypeScript

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

- Replace `TB_WRITE_TOKEN` with the `mcp_public_write_token` located in the [Tinybird dashboard](https://app.tinybird.co/tokens).
- Your `TB_API_URL` is the URL of your Tinybird region. See [Regions and endpoints](https://www.tinybird.co/docs/api-reference#regions-and-endpoints).

To properly process your log events, add the following keys to the `record` JSON object:

```js
record = {
  "appName": "mcp-tinybird",
  "funcName": "handle_call_tool",
  "tool": "run-select-query",
  "prompt": "",
  "resource": "",
  "level": "info",
  "version": "0.1.4",
  "message": "this is a message"
}
```

### Monitor with Grafana and Prometheus

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
