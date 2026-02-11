from fastmcp import FastMCP

mcp = FastMCP("MyMCP")

@mcp.tool(description="A tool that greets a user by name")
def greet(name: str) -> str:
  return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
