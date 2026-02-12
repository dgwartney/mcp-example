# Integrating with Kore AI Agent Platform

This guide explains how to configure and deploy this MCP server as a tool in the Kore AI Agent Platform.

**Author:** David Gwartney (david.gwartney@gmail.com)

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
  - [Option 1: Local Development with ngrok](#option-1-local-development-with-ngrok)
  - [Option 2: Docker Deployment](#option-2-docker-deployment)
  - [Option 3: Cloud Platform Deployment](#option-3-cloud-platform-deployment)
- [Configuring in Kore AI](#configuring-in-kore-ai)
- [Testing the Integration](#testing-the-integration)
- [Managing API Keys](#managing-api-keys)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

The Kore AI Agent Platform uses the Model Context Protocol (MCP) to integrate with external tools and services. This MCP server provides:

- **Authentication**: SQLite-backed API key validation
- **Tools**: Extensible tool framework (includes `greet` tool for demonstration)
- **Transport**: HTTP-based MCP protocol (required for Kore AI)
- **Security**: Case-insensitive header authentication with RFC 7230 compliance

### How It Works with Kore AI

1. **Tool Discovery**: Kore AI connects to your MCP server and discovers available tools
2. **Intent Detection**: The LLM identifies when to use your tools based on user queries
3. **Invocation**: Kore AI sends structured requests with tool name and parameters
4. **Execution**: Your MCP server executes the tool logic and returns results
5. **Response**: The agent formulates a natural language response using the tool output

**Important**: Kore AI requires HTTP-based MCP servers. The default stdio transport is not supported.

---

## Prerequisites

Before integrating with Kore AI, ensure you have:

- ✅ Python 3.12+
- ✅ `uv` package manager installed
- ✅ This MCP server repository cloned and dependencies installed
- ✅ A publicly accessible URL for your server (via ngrok, cloud deployment, etc.)
- ✅ Access to a Kore AI Agent Platform account

---

## Quick Start

For the impatient, here's the fastest path to integration:

```bash
# 1. Install dependencies
uv sync

# 2. Start the server (will generate API key)
uv run fastmcp run my_server.py --transport http --port 8000 --host 0.0.0.0

# 3. Note the API key printed on first run
# Output: Generated default API key: QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80

# 4. In another terminal, expose via ngrok
ngrok http 8000

# 5. Use the ngrok URL in Kore AI configuration
```

Continue reading for detailed deployment options and configuration steps.

---

## Deployment Options

Choose the deployment option that best fits your needs:

| Option | Best For | Complexity | Production Ready |
|--------|----------|------------|------------------|
| **ngrok** | Quick testing, demos | Low | ⚠️ Development only |
| **Docker** | Consistent environments | Medium | ✅ Yes |
| **Cloud Platform** | Scalable production | Medium | ✅ Yes |

### Option 1: Local Development with ngrok

**Best for**: Quick testing, development, and proof-of-concept.

#### Step 1: Install ngrok

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

#### Step 2: Start the MCP Server

```bash
# Start the server with HTTP transport
uv run fastmcp run my_server.py --transport http --port 8000 --host 0.0.0.0
```

**On first run**, the server will generate and print an API key:

```
Generated default API key: QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80
```

**⚠️ IMPORTANT**: Save this API key! You'll need it for Kore AI configuration.

#### Step 3: Create ngrok Tunnel

In a **new terminal window**:

```bash
ngrok http 8000
```

You'll see output like:

```
Forwarding   https://abc123.ngrok.app -> http://localhost:8000
```

**Note the HTTPS URL** - this is your public MCP server endpoint.

#### Step 4: Test the Endpoint

Verify your server is accessible:

```bash
curl -X POST https://abc123.ngrok.app/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

Expected response should list available tools including `greet`.

### Option 2: Docker Deployment

**Best for**: Production deployments, consistent environments, easy scaling.

#### Step 1: Create Dockerfile

Use the provided Dockerfile (or create it):

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

#### Step 2: Build and Run Container

```bash
# Build the Docker image
docker build -t mcp-server .

# Run with persistent database
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e MCP_DB_PATH=/app/data/api_keys.db \
  --name mcp-server \
  mcp-server
```

#### Step 3: Get the API Key

```bash
# Check container logs for the generated API key
docker logs mcp-server
```

Look for the line:
```
Generated default API key: QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80
```

#### Step 4: Deploy to Cloud

Deploy your Docker container to a cloud provider:

- **AWS ECS/Fargate**: Use AWS Container Service
- **Google Cloud Run**: Automatic HTTPS and scaling
- **Azure Container Instances**: Simple container deployment
- **DigitalOcean App Platform**: Git-based deployment

Make note of the public URL provided by your cloud platform.

### Option 3: Cloud Platform Deployment

**Best for**: Production use without Docker complexity.

#### Railway Deployment

1. **Create `Procfile`**:
   ```
   web: uv run fastmcp run my_server.py --transport http --port $PORT --host 0.0.0.0
   ```

2. **Deploy**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login and deploy
   railway login
   railway init
   railway up
   ```

3. **Configure Environment**:
   - Set `MCP_DB_PATH` if needed (Railway provides persistent volumes)
   - Note the Railway-provided public URL

4. **Get API Key**:
   ```bash
   railway logs
   ```

#### Render / Fly.io Deployment

Similar process:
1. Create `Procfile` as above
2. Connect your repository
3. Configure environment variables
4. Deploy and note the public URL
5. Check logs for the generated API key

---

## Configuring in Kore AI

Once your MCP server is deployed and accessible via HTTPS, configure it in Kore AI.

### Step 1: Access Tools Section

1. Log in to your Kore AI Agent Platform account
2. Navigate to your Agentic App
3. Go to the **Tools** section
4. Click **Add Tool** → **+New Tool**

### Step 2: Select MCP Server Type

1. Choose **MCP Server** as the tool type
2. Select **HTTP** as the transport method (not SSE)

### Step 3: Enter Server Details

Fill in the configuration form:

| Field | Value | Example |
|-------|-------|---------|
| **Name** | `mcp-examples` | Unique identifier for your server |
| **Description** | `MCP server with greeting tool` | Brief description of capabilities |
| **Server URL** | Your deployment URL + `/mcp` | `https://abc123.ngrok.app/mcp` |

**⚠️ IMPORTANT**: Always append `/mcp` to your server URL - this is the MCP endpoint path.

### Step 4: Configure Authentication

1. Click the **Configure** button next to "Request Definition"
2. Navigate to the **Headers** section
3. Add a new header:
   - **Name**: `X-API-Key`
   - **Value**: Your API key (from server startup logs)
   - **Description**: `API key for authentication`

**Example**:
```
Name: X-API-Key
Value: QBMDHIqbf_qQV8uW7wJ6sMNDAj2q7VoFS_u9IGVqX80
```

### Step 5: Test Connection

1. Click the **Test** button at the bottom of the configuration page
2. Kore AI will attempt to connect to your server
3. Verify you see a success message and available tools are listed

**Expected result**: You should see the `greet` tool discovered.

### Step 6: Select Tools

1. From the list of discovered tools, check the box next to `greet`
2. Click **Add Selected** to import the tool into your agent

**Note**: Kore AI will automatically prefix the tool name: `mcp-examples__greet`

### Step 7: Save Configuration

1. Review your configuration
2. Click **Save** or **Add Tool** to finalize
3. The tool is now available for your AI agent to use

---

## Testing the Integration

After configuration, test the integration to ensure everything works correctly.

### In Kore AI Platform

1. Open your agent in **Preview** mode
2. Navigate to the **Tools** section
3. Find `mcp-examples__greet` in the list
4. Click **Run Sample Execution**

#### Sample Test Input

Enter the following JSON in the input field:

```json
{
  "name": "Alice"
}
```

Click **Execute**.

#### Expected Sample Response

```json
{
  "content": [
    {
      "type": "text",
      "text": "Hello, Alice!"
    }
  ]
}
```

### Via Conversational Interface

Test the tool through natural conversation:

**User**: "Can you greet someone named Bob?"

**Agent**: The agent should recognize the intent, invoke the `mcp-examples__greet` tool with `name: "Bob"`, and respond: "Hello, Bob!"

### Direct API Testing

Test your MCP server directly (outside Kore AI) to isolate issues:

```bash
# Test tool discovery
curl -X POST https://your-server.com/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# Test greet tool invocation
curl -X POST https://your-server.com/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "greet",
      "arguments": {
        "name": "Charlie"
      }
    },
    "id": 2
  }'
```

---

## Managing API Keys

### Viewing Existing Keys

```bash
sqlite3 api_keys.db "SELECT * FROM api_keys;"
```

### Adding Additional Keys

Generate a new secure key and add it:

```bash
# Generate a cryptographically secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to database
sqlite3 api_keys.db "INSERT INTO api_keys (key) VALUES ('NEW_KEY_HERE');"
```

### Rotating Keys

For production environments, implement key rotation:

1. **Add a new key** (don't remove the old one yet)
2. **Update Kore AI** configuration with the new key
3. **Test** the integration thoroughly
4. **Remove the old key** from the database:
   ```bash
   sqlite3 api_keys.db "DELETE FROM api_keys WHERE key = 'OLD_KEY';"
   ```

### Revoking Keys

Immediately revoke compromised keys:

```bash
sqlite3 api_keys.db "DELETE FROM api_keys WHERE key = 'COMPROMISED_KEY';"
```

**⚠️ WARNING**: Revoking a key will immediately break any integrations using it.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Connection Failed" in Kore AI

**Symptoms**: Test button shows connection error.

**Possible Causes**:
- Server not running or not accessible
- Incorrect URL (missing `/mcp` endpoint)
- Firewall blocking external access
- ngrok tunnel expired (free tier has 2-hour limit)

**Solutions**:
```bash
# Verify server is running
curl https://your-server.com/mcp

# Check server logs
docker logs mcp-server  # For Docker
railway logs            # For Railway
heroku logs --tail      # For Heroku

# Restart ngrok (if using)
ngrok http 8000
```

#### 2. "Unauthorized: Invalid or missing API Key"

**Symptoms**: Connection succeeds but tool discovery fails.

**Possible Causes**:
- API key not configured in headers
- Incorrect API key value
- Key was deleted from database

**Solutions**:
1. Verify the API key in Kore AI configuration matches database:
   ```bash
   sqlite3 api_keys.db "SELECT * FROM api_keys;"
   ```

2. Check header configuration:
   - Header name must be exactly `X-API-Key` (case-insensitive)
   - Value must match a key in the database

3. Regenerate if lost:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   sqlite3 api_keys.db "INSERT INTO api_keys (key) VALUES ('NEW_KEY');"
   ```

#### 3. "No Tools Discovered"

**Symptoms**: Connection succeeds but no tools appear.

**Possible Causes**:
- Server code issue
- Wrong MCP protocol implementation
- Tool registration failed

**Solutions**:
```bash
# Verify tools are registered
curl -X POST https://your-server.com/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Check server logs for errors
# Restart server if needed
```

#### 4. "Tool Invocation Failed"

**Symptoms**: Tool discovered but execution fails.

**Possible Causes**:
- Invalid parameters passed
- Server-side error
- Timeout issues

**Solutions**:
1. Test the tool directly:
   ```bash
   curl -X POST https://your-server.com/mcp \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_KEY" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "greet",
         "arguments": {"name": "Test"}
       },
       "id": 2
     }'
   ```

2. Check parameter format matches tool schema
3. Review server logs for errors

#### 5. ngrok Tunnel Issues

**Symptoms**: "Tunnel not found" or connection drops.

**Possible Causes**:
- Free tier tunnel expired (2-hour limit)
- ngrok process stopped
- Network connectivity issues

**Solutions**:
```bash
# Restart ngrok
pkill ngrok
ngrok http 8000

# For longer sessions, consider ngrok paid tier
# Or use a permanent cloud deployment instead
```

#### 6. Database File Not Found

**Symptoms**: Server fails to start with database error.

**Possible Causes**:
- Database path incorrect
- Permissions issue
- Volume not mounted (Docker)

**Solutions**:
```bash
# Check database path
echo $MCP_DB_PATH

# Set explicitly
export MCP_DB_PATH=/app/data/api_keys.db

# For Docker, verify volume mount
docker run -v $(pwd)/data:/app/data ...

# Check file permissions
ls -la api_keys.db
chmod 644 api_keys.db
```

---

## Best Practices

### Security

1. **Use HTTPS Only**: Never expose your MCP server over plain HTTP in production
2. **Rotate Keys Regularly**: Change API keys every 90 days
3. **Monitor Access**: Keep logs of all API key usage
4. **Separate Keys by Environment**: Use different keys for dev/staging/production
5. **Backup Database**: Regularly backup `api_keys.db`
   ```bash
   # Backup command
   cp api_keys.db api_keys.db.backup-$(date +%Y%m%d)
   ```

### Deployment

1. **Use Environment Variables**: Store `MCP_DB_PATH` in environment, not code
2. **Persistent Storage**: Ensure database survives container restarts
3. **Health Checks**: Implement monitoring to detect server failures
4. **Logging**: Enable comprehensive logging for troubleshooting:
   ```bash
   # Redirect logs to file
   uv run fastmcp run my_server.py --transport http --port 8000 > server.log 2>&1
   ```
5. **Containerize for Production**: Use Docker for consistent deployments

### Kore AI Integration

1. **Descriptive Naming**: Use clear, descriptive names for MCP servers in Kore AI
2. **Document Tools**: Add detailed descriptions for each tool in your server code
3. **Test Thoroughly**: Always test tools in Preview mode before production
4. **Manual Refresh**: Remember to refresh in Kore AI after updating server tools
5. **Enable Artifacts**: Turn on "Include Tool Response in Artifacts" for debugging
6. **Version Control**: Tag server versions to track which version Kore AI is using

### Scaling

1. **Horizontal Scaling**: Deploy multiple instances behind a load balancer
2. **Database Replication**: For high availability, consider database replication
3. **Caching**: Add caching layer for frequently accessed data
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Monitoring**: Use application performance monitoring (APM) tools

---

## Adding More Tools

The included `greet` tool is a simple example. To add more tools:

### 1. Edit `my_server.py`

Add new tool definitions in the `_register_tools` method:

```python
def _register_tools(self) -> None:
    @self.mcp.tool(description="A tool that greets a user by name")
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    @self.mcp.tool(description="Get the current server time")
    def get_time() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()

    @self.mcp.tool(description="Add two numbers together")
    def add(a: int, b: int) -> int:
        return a + b
```

### 2. Restart the Server

```bash
# Stop the current server (Ctrl+C)
# Restart with new tools
uv run fastmcp run my_server.py --transport http --port 8000 --host 0.0.0.0
```

### 3. Refresh in Kore AI

**⚠️ IMPORTANT**: Kore AI does not automatically detect server changes.

1. Go to the **Tools** section in Kore AI
2. Find your MCP server configuration
3. Click the **refresh icon** (↻) next to the server name
4. Verify new tools appear in the list
5. Select and add the new tools

### 4. Test New Tools

Use the Preview mode to test each new tool with sample inputs.

---

## Next Steps

- **Add Real Functionality**: Replace the demo `greet` tool with your actual business logic
- **Implement Error Handling**: Add proper error responses for tool failures
- **Add Input Validation**: Validate tool parameters before processing
- **Create Multiple Servers**: Deploy separate MCP servers for different capabilities
- **Monitor Performance**: Set up monitoring and alerting for your production server
- **Document Your Tools**: Provide clear descriptions and examples for each tool

---

## Additional Resources

- **MCP Specification**: [https://spec.modelcontextprotocol.io/](https://spec.modelcontextprotocol.io/)
- **FastMCP Documentation**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Kore AI Documentation**: [https://docs.kore.ai](https://docs.kore.ai)
- **Project README**: See `README.md` for detailed server documentation

---

## Support

For issues with:
- **This MCP Server**: Open an issue in the project repository
- **Kore AI Platform**: Contact Kore AI support
- **FastMCP Library**: Visit the FastMCP GitHub repository

---

**Last Updated**: February 2026
**Document Version**: 1.0.0
