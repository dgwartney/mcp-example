import os
import secrets
import sqlite3

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
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

    def validate_key(self, api_key: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT 1 FROM api_keys WHERE key = ?", (api_key,)
            ).fetchone()
        finally:
            conn.close()
        return row is not None


class ApiKeyMiddleware(Middleware):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()

        # HTTP headers are case-insensitive per RFC 7230
        # Create a case-insensitive lookup
        headers_lower = {k.lower(): v for k, v in headers.items()}
        api_key = headers_lower.get("x-api-key")

        if not self.db_manager.validate_key(api_key):
            raise ToolError("Unauthorized: Invalid or missing API Key")

        return await call_next(context)


class MCPServer:
    def __init__(self, name: str = "MyMCP", db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.db")

        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_db()

        self.mcp = FastMCP(name)
        self.mcp.add_middleware(ApiKeyMiddleware(self.db_manager))
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool(description="A tool that greets a user by name")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

    def run(self):
        self.mcp.run()


server = MCPServer()
mcp = server.mcp  # FastMCP CLI expects a module-level 'mcp' object

if __name__ == "__main__":
    server.run()
