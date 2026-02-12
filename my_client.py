"""
FastMCP Client for calling remote MCP tools with API key authentication.

This module implements a client for the Model Context Protocol (MCP) using
the FastMCP library. It demonstrates how to connect to a remote MCP server,
authenticate using API keys via HTTP headers, and invoke server-side tools.

Example:
    Basic usage with required API key:
        $ python my_client.py --api-key YOUR_API_KEY

    Custom name and server URL:
        $ python my_client.py --api-key YOUR_API_KEY --name Alice --url http://localhost:8000/mcp

    Using uv for dependency management:
        $ uv run my_client.py --api-key YOUR_API_KEY
"""

import argparse
import asyncio
from typing import Any, Dict

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPClient:
    """
    Client for connecting to and calling tools on a remote MCP server.

    This class handles the connection setup, authentication via API keys,
    and tool invocation. It uses StreamableHttpTransport to pass custom
    headers for authentication.

    Attributes:
        url (str): The MCP server URL endpoint.
        api_key (str): API key for authentication via X-API-Key header.
    """

    def __init__(self, url: str, api_key: str):
        """
        Initialize the MCP client.

        Args:
            url (str): The MCP server URL (e.g., "http://localhost:8000/mcp").
            api_key (str): API key for authentication.
        """
        self.url = url
        self.api_key = api_key

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the remote MCP server.

        Establishes a connection to the MCP server using StreamableHttpTransport
        with the API key in the X-API-Key header, then invokes the specified tool.

        Args:
            tool_name (str): Name of the tool to call on the server.
            arguments (Dict[str, Any]): Dictionary of arguments to pass to the tool.

        Returns:
            Any: The result returned by the tool.

        Raises:
            Exception: If the connection fails or the tool invocation encounters an error.
        """
        transport = StreamableHttpTransport(
            self.url,
            headers={"X-API-Key": self.api_key}
        )
        client = Client(transport)
        async with client:
            result = await client.call_tool(tool_name, arguments)
            return result

    async def greet(self, name: str) -> None:
        """
        Call the 'greet' tool on the server and print the result.

        This is a convenience method for calling the greet tool specifically.

        Args:
            name (str): The name to pass to the greet tool.

        Raises:
            Exception: If the tool call fails.
        """
        result = await self.call_tool("greet", {"name": name})
        print(result)


class MCPClientApp:
    """
    Command-line application for the MCP client.

    Handles argument parsing and execution flow for the MCP client.
    Provides a CLI interface for connecting to MCP servers and calling tools.

    Attributes:
        parser (argparse.ArgumentParser): Command-line argument parser.
    """

    def __init__(self):
        """Initialize the CLI application with argument parser."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure the argument parser.

        Returns:
            argparse.ArgumentParser: Configured parser with all CLI arguments.
        """
        parser = argparse.ArgumentParser(
            description="FastMCP client for calling remote tools",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --api-key abc123xyz
  %(prog)s --api-key abc123xyz --name Alice
  %(prog)s --api-key abc123xyz --url http://localhost:8000/mcp --name Bob
            """
        )
        parser.add_argument(
            "--api-key",
            required=True,
            help="API key for authentication (required)"
        )
        parser.add_argument(
            "--name",
            default="Ford",
            help="Name to greet (default: Ford)"
        )
        parser.add_argument(
            "--url",
            default="https://my-service.ngrok.app/mcp",
            help="MCP server URL (default: https://my-service.ngrok.app/mcp)"
        )
        return parser

    def run(self) -> None:
        """
        Parse arguments and run the client.

        Parses command-line arguments, creates an MCPClient instance,
        and calls the greet tool. Handles and displays any errors that occur.
        """
        args = self.parser.parse_args()
        client = MCPClient(args.url, args.api_key)

        try:
            asyncio.run(client.greet(args.name))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    app = MCPClientApp()
    app.run()
