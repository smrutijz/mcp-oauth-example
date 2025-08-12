from fastmcp import FastMCP
from oauth import OAuthMiddleware


mcp = FastMCP("OAuthMCPDemo")
mcp.add_middleware(OAuthMiddleware())

@mcp.tool
async def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000, stateless_http=False, transport="streamable-http")
