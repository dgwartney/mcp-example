# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) examples using the FastMCP Python library. The project demonstrates building MCP servers with tools and middleware-based authentication, plus a client for calling those tools remotely.

## Setup & Commands

This project uses `uv` for Python package management with Python 3.12.

```bash
# Install dependencies
uv sync

# Run the MCP server (starts with default stdio transport)
uv run my_server.py

# Run the MCP client
uv run my_client.py
```

## Architecture

- **my_server.py** — FastMCP server that registers tools (e.g., `greet`) and applies API key authentication via middleware. The `ApiKeyMiddleware` checks for an `X-API-Key` header on incoming HTTP requests.
- **my_client.py** — FastMCP client that connects to a remote MCP endpoint and calls tools.
- **auth.py** — Standalone snippet of the `ApiKeyMiddleware` class (no imports; reference/example code, not directly runnable).

## Key Dependencies

- `fastmcp>=2.14.5` — The core library for both server and client. Provides `FastMCP`, `Client`, `Middleware`, `ToolError`, and `get_http_headers`.
