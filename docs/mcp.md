# MCP server

The engine can run as a [Model Context Protocol](https://modelcontextprotocol.io)
server, so a Claude-based clinical assistant can call it as a real-time tool
while drafting a note. It is a thin wrapper over the tested registry and
dispatch layers — stateless, no storage, no input logging, with a
*not-a-medical-device* disclaimer on every result.

## Install

The MCP SDK is an optional extra (the core stays standard-library-only):

```bash
pip install ".[mcp]"
```

## Run

```bash
python -m engine.mcp_server
```

This serves over stdio — the transport MCP clients launch.

## Tools

| Tool | Purpose |
|---|---|
| `list_conditions` | Catalog: each algorithm's key, label, and presentation tags |
| `list_presentations` | The presentation tags the catalog is indexed by |
| `get_condition_schema` | JSON Schema of one condition's input features |
| `describe_condition` | A condition's full record (label, presentations, schema) |
| `run_algorithm` | Run one algorithm over its structured features |
| `suggest_algorithms` | Rank algorithms by how close they are to runnable on a feature bag |
| `run_applicable` | Run every algorithm a feature bag satisfies; report what needs more data |

`run_algorithm` returns `{"ok": true, "result": ...}` on success, or
`{"ok": false, "error": ..., "missing_inputs": [...]}` so the assistant can ask
the clinician for what's missing instead of failing.

## Register with a client (example)

For a Claude Code / Claude Desktop style `mcpServers` config:

```json
{
  "mcpServers": {
    "care-algorithms": {
      "command": "python",
      "args": ["-m", "engine.mcp_server"]
    }
  }
}
```

## Boundary

The server accepts only **structured features** (numbers, booleans, enums) — never
raw clinical notes. Turning a note into those features is the job of the optional
extraction adapter (Phase 5), which runs in the caller's secure environment. See
[docs/architecture.md](architecture.md).
