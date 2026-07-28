"""Minimal authenticated MCP HTTP adapter for the /watch skill.

This adapter deliberately keeps the upstream skill as the processing engine.
It is a deployment starting point, not a public unauthenticated service.
"""
from __future__ import annotations

import ipaddress
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP, Context


mcp = FastMCP("claude-video-watch", stateless_http=True, json_response=True)
SCRIPT = Path("/app/skills/watch/scripts/watch.py")
TOKEN = os.environ.get("MCP_AUTH_TOKEN", "")
MAX_URL_LENGTH = int(os.environ.get("MAX_URL_LENGTH", "2048"))
MAX_FRAMES = int(os.environ.get("MAX_FRAMES", "100"))
TIMEOUT_SECONDS = int(os.environ.get("JOB_TIMEOUT_SECONDS", "900"))


def _authorized(ctx: Context) -> None:
    if not TOKEN:
        raise RuntimeError("MCP_AUTH_TOKEN is not configured")
    request = getattr(ctx, "request_context", None)
    headers = getattr(getattr(request, "request", None), "headers", {})
    supplied = headers.get("authorization", "")
    if supplied != f"Bearer {TOKEN}":
        raise PermissionError("Unauthorized")


def _validate_url(source: str) -> None:
    if len(source) > MAX_URL_LENGTH:
        raise ValueError("URL is too long")
    parsed = urlparse(source)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only absolute http(s) URLs are accepted")
    host = parsed.hostname.lower().rstrip(".")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        raise ValueError("Private, loopback, link-local, and reserved IPs are blocked")
    if host in {"localhost", "localhost.localdomain"}:
        raise ValueError("Local hostnames are blocked")


@mcp.tool()
def watch_video(url: str, question: str = "Summarize this video", detail: str = "balanced", ctx: Context | None = None) -> str:
    """Download a public video URL, extract evidence, and return a grounded report."""
    if ctx is not None:
        _authorized(ctx)
    _validate_url(url)
    if detail not in {"transcript", "efficient", "balanced", "token-burner"}:
        raise ValueError("Invalid detail mode")
    with tempfile.TemporaryDirectory(prefix="watch-job-", dir="/tmp/claude-video") as work:
        command = [
            "python", str(SCRIPT), url, "--detail", detail,
            "--max-frames", str(MAX_FRAMES), "--out-dir", work,
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-4000:] or "Video processing failed")
        report = result.stdout.strip()
        return f"Question: {question}\n\n{report}\n\nSecurity note: temporary files were deleted after processing."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

