# Integration Matrix

## Default public integration

| Integration | Default | Why |
| --- | --- | --- |
| Meting-Agent | Enabled | Publicly installable and directly relevant to reference music search |

## Optional sidecar integrations

| Integration | Default | Why |
| --- | --- | --- |
| midi-composer-mcp | Disabled | Very high value for deterministic theory/composition tools, but best introduced as explicit sidecar |
| reaper-mcp | Disabled | Strong advanced backend for REAPER users only |

## Optional advanced integrations

| Integration | Default | Why not default |
| --- | --- | --- |
| Memory / Hindsight | Disabled | Server-specific state and persistence concerns |
| Embedding service | Disabled | Extra process and data lifecycle complexity |
| Browser / Research tooling | Disabled | Useful for research, not required for core generation |

## Not integrated into runtime

| Tool family | Decision | Reason |
| --- | --- | --- |
| Codegraph / codebase MCP | Not integrated | Development tooling, not product runtime |
| Office / generic MCP tooling | Not integrated | Unrelated to core music workflow |
| AiToEarn | Excluded per current scope | User explicitly excluded it from this integration pass |
