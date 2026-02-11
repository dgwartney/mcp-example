import argparse
import asyncio
from fastmcp import Client

async def call_tool(api_key: str, name: str):
    client = Client(
        "https://my-service.ngrok.app/mcp",
        headers={"X-API-Key": api_key}
    )
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

def main():
    parser = argparse.ArgumentParser(description="FastMCP client for calling remote tools")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--name", default="Ford", help="Name to greet (default: Ford)")
    args = parser.parse_args()

    try:
        asyncio.run(call_tool(args.api_key, args.name))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
