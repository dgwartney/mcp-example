"""
FastMCP Server with SQLite-backed API Key Authentication.

This module implements a Model Context Protocol (MCP) server using the FastMCP
library with middleware-based authentication. API keys are stored and validated
against a SQLite database.

Author:
    David Gwartney <david.gwartney@gmail.com>

Environment Variables:
    MCP_DB_PATH: Optional path to SQLite database file.
                 Defaults to api_keys.db in the script's directory if not set.

Example:
    Run the server directly:
        $ uv run my_server.py

    Run via FastMCP CLI:
        $ uv run fastmcp run my_server.py

    Run as HTTP server:
        $ uv run fastmcp run my_server.py --transport http --port 8000

    Run with custom database path:
        $ MCP_DB_PATH=/var/data/keys.db uv run my_server.py
"""

import os
import secrets
import sqlite3
from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError


class DatabaseManager:
    """
    Manages SQLite database operations for API key storage and validation.

    This class handles database initialization, API key generation, and
    validation against stored keys. Keys are stored securely using
    parameterized queries to prevent SQL injection.

    Attributes:
        db_path (str): Path to the SQLite database file.
    """

    def __init__(self, db_path: str):
        """
        Initialize the DatabaseManager.

        Args:
            db_path (str): Absolute path to the SQLite database file.
        """
        self.db_path = db_path

    def init_db(self) -> None:
        """
        Initialize the database schema and create a default API key.

        Creates the api_keys table if it doesn't exist. If the table is empty,
        generates a cryptographically secure random API key using secrets.token_urlsafe()
        and inserts it as the default key. The generated key is printed to stdout
        on first run.

        The table schema:
            - id: INTEGER PRIMARY KEY AUTOINCREMENT
            - key: TEXT UNIQUE NOT NULL

        Raises:
            sqlite3.Error: If database operations fail.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS api_keys "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL)"
            )
            row = conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()
            if row[0] == 0:
                default_key = secrets.token_urlsafe(32)
                conn.execute("INSERT INTO api_keys (key) VALUES (?)", (default_key,))
                print(f"Generated default API key: {default_key}")
            conn.commit()
        finally:
            conn.close()

    def validate_key(self, api_key: Optional[str]) -> bool:
        """
        Validate an API key against the database.

        Args:
            api_key (Optional[str]): The API key to validate. Can be None.

        Returns:
            bool: True if the key exists in the database, False otherwise.

        Raises:
            sqlite3.Error: If database query fails.
        """
        if api_key is None:
            return False

        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT 1 FROM api_keys WHERE key = ?", (api_key,)
            ).fetchone()
        finally:
            conn.close()
        return row is not None


class ApiKeyMiddleware(Middleware):
    """
    Middleware for validating API keys on incoming requests.

    This middleware extracts the X-API-Key header from HTTP requests and
    validates it against the database. Header matching is case-insensitive
    per RFC 7230. Requests with invalid or missing API keys are rejected.

    Attributes:
        db_manager (DatabaseManager): Database manager instance for key validation.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the ApiKeyMiddleware.

        Args:
            db_manager (DatabaseManager): Database manager for API key validation.
        """
        self.db_manager = db_manager

    async def on_request(self, context: MiddlewareContext, call_next):
        """
        Process incoming requests and validate API keys.

        Extracts the X-API-Key header (case-insensitive) from the request,
        validates it against the database, and either continues processing
        or raises an error for invalid keys.

        Args:
            context (MiddlewareContext): The request context.
            call_next: Callable to invoke the next middleware or tool handler.

        Returns:
            The result from call_next if authentication succeeds.

        Raises:
            ToolError: If the API key is invalid or missing.
        """
        headers = get_http_headers()

        # HTTP headers are case-insensitive per RFC 7230
        # Create a case-insensitive lookup
        headers_lower = {k.lower(): v for k, v in headers.items()}
        api_key = headers_lower.get("x-api-key")

        if not self.db_manager.validate_key(api_key):
            raise ToolError("Unauthorized: Invalid or missing API Key")

        return await call_next(context)


class MCPServer:
    """
    FastMCP server with API key authentication.

    Encapsulates the entire MCP server setup including database initialization,
    middleware registration, and tool registration. The server can be run
    via stdio transport (default) or HTTP transport when using the FastMCP CLI.

    Attributes:
        db_manager (DatabaseManager): Manages API key database operations.
        mcp (FastMCP): The FastMCP server instance.
    """

    def __init__(self, name: str = "MyMCP", db_path: Optional[str] = None):
        """
        Initialize the MCP server.

        Args:
            name (str, optional): Name of the MCP server. Defaults to "MyMCP".
            db_path (Optional[str], optional): Path to the SQLite database.
                If None, checks MCP_DB_PATH environment variable.
                If not set, defaults to api_keys.db in the script's directory.
                Defaults to None.
        """
        if db_path is None:
            db_path = os.environ.get(
                "MCP_DB_PATH",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.db")
            )

        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_db()

        self.mcp = FastMCP(name)
        self.mcp.add_middleware(ApiKeyMiddleware(self.db_manager))
        self._register_tools()

    def _register_tools(self) -> None:
        """
        Register MCP tools with the server.

        This method registers all available tools that can be called by clients.
        Currently implements a single 'greet' tool for demonstration purposes.
        """
        @self.mcp.tool(description="A tool that greets a user by name")
        def greet(name: str) -> str:
            """
            Generate a greeting message.

            Args:
                name (str): The name of the person to greet.

            Returns:
                str: A greeting message in the format "Hello, {name}!".
            """
            return f"Hello, {name}!"

    def run(self) -> None:
        """
        Run the MCP server.

        Starts the FastMCP server using the configured transport.
        Blocks until the server is shut down.
        """
        self.mcp.run()


# Module-level instances
server = MCPServer()
mcp = server.mcp  # FastMCP CLI expects a module-level 'mcp' object

if __name__ == "__main__":
    server.run()
