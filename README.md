# MCP Examples

A production-ready implementation of Model Context Protocol (MCP) server and client using FastMCP with SQLite-backed API key authentication.

**Author:** David Gwartney (david.gwartney@gmail.com)

## Overview

This project demonstrates how to build secure MCP servers and clients with:

- **SQLite-backed Authentication**: API keys stored and validated against a SQLite database
- **Middleware-based Security**: Clean separation of concerns with reusable authentication middleware
- **Case-insensitive Headers**: RFC 7230-compliant header handling
- **Class-based Architecture**: Modular, testable, and maintainable code structure
- **Cryptographic Key Generation**: Secure random API keys using Python's `secrets` module
- **Comprehensive Testing**: 61 unit tests with >90% code coverage

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

### Testing (`test_*.py`)

- **61 Unit Tests**: Comprehensive test coverage for all components
- **96.49% Server Coverage**: Database, middleware, and server classes fully tested
- **100% Client Coverage**: Client and CLI application completely tested
- **Async Test Support**: Proper testing of async/await patterns
- **Integration Tests**: End-to-end workflow validation
- **CI/CD Ready**: XML and HTML coverage reports for continuous integration

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
- `uv` package manager (handles all dependencies and virtual environments)
- FastMCP 2.14.5+ (installed via uv)

## Installation

This project uses `uv` for Python package management and virtual environment handling.

### Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via Homebrew (macOS)
brew install uv

# Or via pip
pip install uv
```

### Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mcp-examples

# Install dependencies (creates virtual environment automatically)
uv sync

# Install with test dependencies
uv sync --extra test
```

**Note**: `uv` automatically creates and manages the virtual environment in `.venv/`. No manual virtual environment creation is needed.

## Usage

### Running the Server

#### Option 1: Direct Python Execution (stdio transport)

```bash
uv run my_server.py
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
uv run my_client.py --api-key YOUR_API_KEY_HERE
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

### Running Tests

The project includes comprehensive unit tests with >90% code coverage for all production code.

#### Test Coverage Summary

| Component | Tests | Coverage | Details |
|-----------|-------|----------|---------|
| **my_server.py** | 31 | 96.49% | Database, middleware, server classes |
| **my_client.py** | 30 | 100% | Client and CLI application |
| **Total** | 61 | 98.90% | All production code covered |

**Test Categories**:
- **Unit Tests**: Individual class and method testing with mocks
- **Integration Tests**: End-to-end workflows and component interactions
- **Edge Cases**: Special inputs, error conditions, unusual scenarios
- **Async Tests**: Proper async/await testing with pytest-asyncio

#### Install Test Dependencies

```bash
uv sync --extra test
```

**Test Dependencies**:
- `pytest>=8.0.0` - Test framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-cov>=7.0.0` - Coverage reporting
- `pytest-mock>=3.12.0` - Mocking utilities

#### Run All Tests

```bash
uv run pytest
```

#### Run Tests with Coverage Report

```bash
# Terminal report with missing lines
uv run pytest --cov=my_server --cov=my_client --cov-report=term-missing

# HTML coverage report (opens in browser)
uv run pytest --cov=my_server --cov=my_client --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI/CD)
uv run pytest --cov=my_server --cov=my_client --cov-report=xml
```

#### Run Specific Test Files

```bash
# Test server only
uv run pytest test_my_server.py

# Test client only
uv run pytest test_my_client.py

# Run specific test class
uv run pytest test_my_server.py::TestDatabaseManager

# Run specific test method
uv run pytest test_my_server.py::TestDatabaseManager::test_init_db_creates_table

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x
```

#### Test Suite Details

**Server Tests (`test_my_server.py`)**:
- `TestDatabaseManager` (9 tests): Database initialization, schema, key validation
- `TestApiKeyMiddleware` (7 tests): Authentication, case-insensitive headers, error handling
- `TestMCPServer` (10 tests): Server initialization, middleware/tool registration
- `TestIntegration` (3 tests): End-to-end authentication workflows

**Client Tests (`test_my_client.py`)**:
- `TestMCPClient` (9 tests): Client initialization, tool calls, error handling
- `TestMCPClientApp` (13 tests): CLI parsing, argument validation, execution
- `TestIntegration` (3 tests): End-to-end client workflows
- `TestEdgeCases` (4 tests): Special characters, unusual inputs, edge cases

#### Example Test Output

```bash
$ uv run pytest --cov=my_server --cov=my_client --cov-report=term-missing

============================= test session starts ==============================
platform darwin -- Python 3.12.12, pytest-9.0.2, pluggy-1.6.0
collected 61 items

test_my_client.py ..............................                         [ 49%]
test_my_server.py ...............................                        [100%]

---------- coverage: platform darwin, python 3.12.12 -----------
Name           Stmts   Miss   Cover   Missing
---------------------------------------------
my_client.py      34      0 100.00%
my_server.py      57      2  96.49%   214, 223
---------------------------------------------
TOTAL             91      2  97.80%

============================== 61 passed in 4.06s ===============================
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
├── test_my_server.py     # Server unit tests (>95% coverage)
├── test_my_client.py     # Client unit tests (>95% coverage)
├── auth.py               # Standalone middleware example (reference)
├── api_keys.db           # SQLite database (generated on first run)
├── pyproject.toml        # Project dependencies (uv)
├── uv.lock               # Dependency lock file
├── pytest.ini            # Pytest configuration
├── .coveragerc           # Coverage configuration
├── CHANGELOG.md          # Version history and changes
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
