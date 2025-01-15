# Tinybird MCP server

[![smithery badge](https://smithery.ai/badge/mcp-tinybird)](https://smithery.ai/server/@tinybirdco/mcp-tinybird)

An MCP server to interact with a Tinybird Workspace from any MCP client.

<a href="https://glama.ai/mcp/servers/53l5ojnx30"><img width="380" height="200" src="https://glama.ai/mcp/servers/53l5ojnx30/badge" alt="Tinybird server MCP server" /></a>

## Features

- Query Tinybird Data Sources using the Tinybird Query API
- Get the result of existing Tinybird API Endpoints with HTTP requests
- Push Datafiles

It supports both SSE and STDIO modes.

## Usage examples

- [Bluesky metrics](https://bsky.app/profile/alasdairb.com/post/3lbx2mq5urk22) ([Claude transcript](https://www.tinybird.co/blog-posts/claude-analyze-bluesky-data-tinybird-mcp-server))
- [Web analytics starter kit metrics](https://github.com/tinybirdco/web-analytics-starter-kit) ([video](https://x.com/alrocar/status/1861849648882688341)]

## Setup

### Installation

#### Using MCP package managers

**Smithery**

To install Tinybird MCP for Claude Desktop automatically via [Smithery](https://smithery.ai/protocol/mcp-tinybird):

```bash
npx @smithery/cli install @tinybirdco/mcp-tinybird --client claude
```

**mcp-get**

You can install the Tinybird MCP server using [mcp-get](https://github.com/michaellatman/mcp-get):

```bash
npx @michaellatman/mcp-get@latest install mcp-tinybird
```

### Prerequisites

MCP is still very new and evolving, we recommend following the [MCP documentation](https://modelcontextprotocol.io/quickstart#prerequisites) to get the MCP basics up and running.

You'll need:
- [Tinybird Account & Workspace](https://www.tinybird.co/)
- [Claude Desktop](https://claude.ai/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Configuration

#### 1. Configure Claude Desktop

Create the following file depending on your OS:

On MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Paste this template in the file and replace `<TINYBIRD_API_URL>` and `<TINYBIRD_ADMIN_TOKEN>` with your Tinybird API URL and Admin Token:

```json
{
    "mcpServers": {
        "mcp-tinybird": {
            "command": "uvx",
            "args": [
                "mcp-tinybird",
                "stdio"
            ],
            "env": {
                "TB_API_URL": "<TINYBIRD_API_URL>",
                "TB_ADMIN_TOKEN": "<TINYBIRD_ADMIN_TOKEN>"
            }
        }
    }
}
```

#### 2. Restart Claude Desktop


#### SSE mode

Alternatively, you can run the MCP server in SSE mode by running the following command:

```bash
uvx mcp-tinybird sse
```

This mode is useful to integrate with an MCP client that supports SSE (like a web app).

## Prompts

The server provides a single prompt:
- [tinybird-default](https://github.com/tinybirdco/mcp-tinybird/blob/93dd9e1d3c0e33f408fe88297151a44c1dfc049c/src/mcp-tinybird/server.py#L20): Assumes you have loaded some data in Tinybird and want help exploring it.
  - Requires a "topic" argument which defines the topic of the data you want to explore, for example, "Bluesky data" or "retail sales".

You can configure additional prompt workflows:
  - Create a prompts Data Source in your workspace with this schema and append your prompts. The MCP loads `prompts` on initialization so you can configure it to your needs:
```bash
SCHEMA >
    `name` String `json:$.name`,
    `description` String `json:$.description`,
    `timestamp` DateTime `json:$.timestamp`,
    `arguments` Array(String) `json:$.arguments[:]`,
    `prompt` String `json:$.prompt`
```

## Tools

The server implements several tools to interact with the Tinybird Workspace:
- `list-data-sources`: Lists all Data Sources in the Tinybird Workspace
- `list-pipes`: Lists all Pipe Endpoints in the Tinybird Workspace
- `get-data-source`: Gets the information of a Data Source given its name, including the schema.
- `get-pipe`: Gets the information of a Pipe Endpoint given its name, including its nodes and SQL transformation to understand what insights it provides.
- `request-pipe-data`: Requests data from a Pipe Endpoints via an HTTP request. Pipe endpoints can have parameters to filter the analytical data.
- `run-select-query`: Allows to run a select query over a Data Source to extract insights.
- `append-insight`: Adds a new business insight to the memo resource
- `llms-tinybird-docs`: Contains the whole Tinybird product documentation, so you can use it to get context about what Tinybird is, what it does, API reference and more.
- `save-event`: This allows to send an event to a Tinybird Data Source. Use it to save a user generated prompt to the prompts Data Source. The MCP server feeds from the prompts Data Source on initialization so the user can instruct the LLM the workflow to follow.
- `analyze-pipe`: Uses the Tinybird analyze API to run a ClickHouse explain on the Pipe Endpoint query and check if indexes, sorting key, and partition key are being used and propose optimizations suggestions
- `push-datafile`: Creates a remote Data Source or Pipe in the Tinybird Workspace from a local datafile. Use the [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) to save files generated by this MCP server.


## Development

### Config
If you are working locally add two environment variables to a `.env` file in the root of the repository:

```sh
TB_API_URL=
TB_ADMIN_TOKEN=
```

For local development, update your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcp-tinybird_local": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/mcp-tinybird",
        "run",
        "mcp-tinybird",
        "stdio"
      ]
    }
  }
}
```

<details>
  <summary>Published Servers Configuration</summary>

  ```json
  "mcpServers": {
    "mcp-tinybird": {
      "command": "uvx",
      "args": [
        "mcp-tinybird"
      ]
    }
  }
  ```
</details>

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/alrocar/gr/mcp-tinybird run mcp-tinybird
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

### Monitoring

To monitor the MCP server, you can use any compatible Prometheus client such as [Grafana](https://grafana.com/). Learn how to monitor your MCP server [here](./mcp-analytics/README.md).

