import argparse
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPClient:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    async def call_tool(self, tool_name: str, arguments: dict):
        transport = StreamableHttpTransport(
            self.url,
            headers={"X-API-Key": self.api_key}
        )
        client = Client(transport)
        async with client:
            result = await client.call_tool(tool_name, arguments)
            return result

    async def greet(self, name: str):
        result = await self.call_tool("greet", {"name": name})
        print(result)


class MCPClientApp:
    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self):
        parser = argparse.ArgumentParser(description="FastMCP client for calling remote tools")
        parser.add_argument("--api-key", required=True, help="API key for authentication")
        parser.add_argument("--name", default="Ford", help="Name to greet (default: Ford)")
        parser.add_argument("--url", default="https://my-service.ngrok.app/mcp", help="MCP server URL")
        return parser

    def run(self):
        args = self.parser.parse_args()
        client = MCPClient(args.url, args.api_key)

        try:
            asyncio.run(client.greet(args.name))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    app = MCPClientApp()
    app.run()
