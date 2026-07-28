# Remote MCP adapter

This directory adds a Dockerized Streamable HTTP MCP adapter around the
upstream `skills/watch` implementation. The original skill and Claude Code
plugin remain unchanged.

## Local smoke setup

```bash
docker build -f remote-mcp/Dockerfile -t claude-video-mcp .
docker run --rm -p 8000:8000 \
  -e MCP_AUTH_TOKEN='replace-with-a-long-random-token' \
  claude-video-mcp
```

For a local container with resource limits, copy `.env.example` to `.env` and
run `docker compose up --build` from this directory. The compose file binds
only to localhost by default; use a TLS reverse proxy for internet access.

Before production use, place the service behind HTTPS and an identity-aware
proxy. Do not expose it publicly without authentication.

## Production controls

Set `MCP_AUTH_TOKEN`, `MAX_FRAMES`, and `JOB_TIMEOUT_SECONDS`. Add a reverse
proxy with TLS, rate limiting, request logging redaction, and an egress policy
that blocks private networks. The container should run as the unprivileged
`appuser` and have bounded CPU, memory, and ephemeral disk.

The current adapter is intentionally URL-only. Local file paths are not
accepted by the remote surface. Temporary job directories are removed by the
context manager after success or failure.

## Claude connection

After deployment, configure the resulting HTTPS MCP endpoint in Claude's
connected MCP settings. Keep the bearer token in the provider's secret store;
never put it in a repository, Docker image, or client-side prompt.

The public endpoint should be treated as a private personal service until an
OAuth flow, per-user quotas, and the frame-artifact layer are implemented.

`mcp-config.example.json` shows the shape of the Claude MCP connection. Replace
the URL and token through the Claude connection settings; do not commit the
example with a real token.

## Important limitation

The upstream skill is designed for a local Claude tool host: it prints local
frame paths for Claude to read. A production remote integration should add a
short-lived authenticated artifact endpoint for selected frames, or return
inline image content through the MCP client. This adapter currently returns the
text report and is therefore best treated as a secure prototype until that
artifact layer is added.
