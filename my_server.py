import os
import secrets
import sqlite3

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.db")


def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
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


class ApiKeyMiddleware(Middleware):
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        api_key = headers.get("X-API-Key")

        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT 1 FROM api_keys WHERE key = ?", (api_key,)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise ToolError("Unauthorized: Invalid or missing API Key")

        return await call_next(context)


init_db()

mcp = FastMCP("MyMCP")
mcp.add_middleware(ApiKeyMiddleware())

@mcp.tool(description="A tool that greets a user by name")
def greet(name: str) -> str:
  return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
