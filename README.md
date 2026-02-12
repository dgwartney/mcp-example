# MCP Examples

A production-ready implementation of Model Context Protocol (MCP) server and client using FastMCP with SQLite-backed API key authentication.

## Overview

This project demonstrates how to build secure MCP servers and clients with:

- **SQLite-backed Authentication**: API keys stored and validated against a SQLite database
- **Middleware-based Security**: Clean separation of concerns with reusable authentication middleware
- **Case-insensitive Headers**: RFC 7230-compliant header handling
- **Class-based Architecture**: Modular, testable, and maintainable code structure
- **Cryptographic Key Generation**: Secure random API keys using Python's `secrets` module

## Features

### Server (`my_server.py`)

- **DatabaseManager**: Handles SQLite operations for API key storage and validation
- **ApiKeyMiddleware**: Validates incoming requests against stored API keys
- **MCPServer**: Encapsulates server setup, tool registration, and lifecycle management
- **Multiple Transport Support**: Runs via stdio (default) or HTTP transport
- **Automatic Database Initialization**: Creates schema and generates default API key on first run

### Client (`my_client.py`)

- **MCPClient**: Manages connections and tool invocation with authentication
- **MCPClientApp**: CLI application with argument parsing
- **StreamableHttpTransport**: Properly passes API keys via HTTP headers
- **Error Handling**: Graceful error reporting for connection and authentication failures

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       MCP Client                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ MCPClientApp (CLI Interface)                           │ │
│  │   ├─ Argument parsing (--api-key, --url, --name)      │ │
│  │   └─ Error handling and user feedback                 │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ MCPClient                                              │ │
│  │   ├─ StreamableHttpTransport (X-API-Key header)       │ │
│  │   └─ Tool invocation (greet, etc.)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │ X-API-Key: <token>
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       MCP Server                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ MCPServer                                              │ │
│  │   ├─ FastMCP instance                                 │ │
│  │   └─ Tool registration                                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ApiKeyMiddleware                                       │ │
│  │   ├─ Extract X-API-Key header (case-insensitive)      │ │
│  │   └─ Validate via DatabaseManager                     │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ DatabaseManager                                        │ │
│  │   ├─ SQLite connection management                     │ │
│  │   ├─ Schema initialization                            │ │
│  │   ├─ Key generation (secrets.token_urlsafe)           │ │
│  │   └─ Key validation (parameterized queries)           │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│              ┌──────────────────────────┐                    │
│              │   api_keys.db (SQLite)   │                    │
│              │  ┌────────────────────┐  │                    │
│              │  │ id | key           │  │                    │
│              │  ├────────────────────┤  │                    │
│              │  │ 1  | abc123...     │  │                    │
│              │  │ 2  | xyz789...     │  │                    │
│              │  └────────────────────┘  │                    │
│              └──────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.12+
- `uv` package manager (recommended) or `pip`
- FastMCP 2.14.5+

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd mcp-examples

# Install dependencies
uv sync
```

### Using pip

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Server

#### Option 1: Direct Python Execution (stdio transport)

```bash
# Using uv
uv run my_server.py

# Using python directly
python my_server.py
```

On first run, the server will generate a default API key and print it to stdout:

```
Generated default API key: QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80
```

**Save this key!** You'll need it for client authentication.

#### Option 2: HTTP Transport (for remote clients)

```bash
# Using uv
uv run fastmcp run my_server.py --transport http --port 8000

# Using fastmcp directly
fastmcp run my_server.py --transport http --port 8000
```

#### Option 3: Using FastMCP CLI Development Server

```bash
fastmcp dev my_server.py
```

### Running the Client

The client requires an API key for authentication. Use the key printed by the server on first run.

#### Basic Usage

```bash
# Using uv
uv run my_client.py --api-key YOUR_API_KEY_HERE

# Using python directly
python my_client.py --api-key YOUR_API_KEY_HERE
```

#### Custom Parameters

```bash
# Custom name
uv run my_client.py --api-key YOUR_API_KEY --name Alice

# Custom server URL
uv run my_client.py --api-key YOUR_API_KEY --url http://localhost:8000/mcp

# All parameters
uv run my_client.py \
  --api-key YOUR_API_KEY \
  --name Bob \
  --url http://localhost:8000/mcp
```

#### Example Output

```bash
$ uv run my_client.py --api-key QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80 --name Alice
Hello, Alice!
```

### Managing API Keys

API keys are stored in `api_keys.db` SQLite database. You can manage keys directly:

#### View Existing Keys

```bash
sqlite3 api_keys.db "SELECT * FROM api_keys;"
```

#### Add a New Key

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to database
sqlite3 api_keys.db "INSERT INTO api_keys (key) VALUES ('YOUR_NEW_KEY');"
```

#### Revoke a Key

```bash
sqlite3 api_keys.db "DELETE FROM api_keys WHERE key = 'KEY_TO_REVOKE';"
```

## Deployment

### Local Development

1. Start the server with HTTP transport:
   ```bash
   uv run fastmcp run my_server.py --transport http --port 8000
   ```

2. Test with the client:
   ```bash
   uv run my_client.py --api-key YOUR_API_KEY --url http://localhost:8000/mcp
   ```

### Production Deployment with ngrok

For exposing your local server to the internet (useful for development and demos):

1. Install ngrok:
   ```bash
   # macOS
   brew install ngrok

   # Or download from https://ngrok.com/download
   ```

2. Start the server:
   ```bash
   uv run fastmcp run my_server.py --transport http --port 8000
   ```

3. Create ngrok tunnel:
   ```bash
   ngrok http 8000
   ```

4. Use the ngrok URL with your client:
   ```bash
   uv run my_client.py \
     --api-key YOUR_API_KEY \
     --url https://YOUR-NGROK-SUBDOMAIN.ngrok.app/mcp
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY my_server.py ./

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run server
CMD ["uv", "run", "fastmcp", "run", "my_server.py", "--transport", "http", "--port", "8000", "--host", "0.0.0.0"]
```

Build and run:

```bash
# Build image
docker build -t mcp-server .

# Run container
docker run -p 8000:8000 -v $(pwd)/api_keys.db:/app/api_keys.db mcp-server
```

### Cloud Deployment

The server can be deployed to any cloud platform that supports Python applications:

#### Railway / Render / Fly.io

1. Add a `Procfile`:
   ```
   web: uv run fastmcp run my_server.py --transport http --port $PORT --host 0.0.0.0
   ```

2. Push to your platform's git repository or use their CLI tools

#### AWS Lambda / Google Cloud Functions

For serverless deployment, you'll need to adapt the server to use the platform's event model. FastMCP supports custom transports for this purpose.

## Security Considerations

### API Key Management

- **Never commit** `api_keys.db` to version control (already in `.gitignore`)
- **Rotate keys regularly** in production environments
- **Use environment variables** for sensitive configuration in production
- **Implement rate limiting** for production deployments
- **Use HTTPS** for all production traffic (ngrok provides this automatically)

### Database Security

- The SQLite database uses parameterized queries to prevent SQL injection
- Keys are stored as plain text in the database - for high-security applications, consider hashing keys
- Ensure proper file permissions on `api_keys.db` (readable only by the server process)

### Header Handling

- The server implements case-insensitive header matching per RFC 7230
- All variations of `X-API-Key` header casing are supported

## Extending the Project

### Adding New Tools

Edit `my_server.py` and add tools in the `_register_tools` method:

```python
def _register_tools(self) -> None:
    @self.mcp.tool(description="A tool that greets a user by name")
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    @self.mcp.tool(description="Add two numbers")
    def add(a: int, b: int) -> int:
        return a + b

    @self.mcp.tool(description="Get current timestamp")
    def timestamp() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()
```

### Custom Authentication

To implement different authentication schemes, create a new middleware class:

```python
class BearerTokenMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        headers_lower = {k.lower(): v for k, v in headers.items()}
        auth_header = headers_lower.get("authorization", "")

        if not auth_header.startswith("Bearer "):
            raise ToolError("Unauthorized: Missing or invalid token")

        token = auth_header[7:]  # Remove "Bearer " prefix
        # Validate token...

        return await call_next(context)
```

### Adding Resources

FastMCP also supports resources (read-only data sources):

```python
@self.mcp.resource("config://settings")
def get_settings() -> str:
    return json.dumps({"version": "1.0", "env": "production"})
```

## Troubleshooting

### Client: "Error: Invalid request parameters"

**Cause**: Headers not passed correctly to the transport layer.

**Solution**: Ensure you're using `StreamableHttpTransport` with headers parameter (already implemented in `my_client.py`).

### Client: "Error: Unauthorized: Invalid or missing API Key"

**Cause**: API key is incorrect or not in the database.

**Solution**:
1. Check the key printed during server first run
2. Verify the key exists in the database:
   ```bash
   sqlite3 api_keys.db "SELECT * FROM api_keys;"
   ```

### Server: "Server object 'mcp' not found"

**Cause**: FastMCP CLI expects a module-level `mcp` variable.

**Solution**: Already fixed in `my_server.py` with:
```python
server = MCPServer()
mcp = server.mcp
```

### Connection Refused

**Cause**: Server not running or wrong URL/port.

**Solution**:
1. Verify server is running: `lsof -i :8000` (on Unix)
2. Check the URL matches the server's address
3. Ensure firewall allows the connection

## Project Structure

```
mcp-examples/
├── my_server.py          # MCP server with authentication
├── my_client.py          # MCP client CLI application
├── auth.py               # Standalone middleware example (reference)
├── api_keys.db           # SQLite database (generated on first run)
├── pyproject.toml        # Project dependencies (uv)
├── uv.lock               # Dependency lock file
├── CLAUDE.md             # Instructions for Claude Code
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- All classes and functions have docstrings (Google style)
- Type hints are used throughout
- Changes maintain backward compatibility
- Security best practices are followed

## License

This project is provided as-is for educational and demonstration purposes.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## Support

For issues, questions, or contributions, please open an issue on the project repository.
