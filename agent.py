import os
import json
import http.client
import urllib.parse
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools

load_dotenv()
OAUTH_DOMAIN_NAME = os.getenv("OAUTH_DOMAIN_NAME")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_bearer_token():
    conn = http.client.HTTPSConnection(OAUTH_DOMAIN_NAME)
    params = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'audience': OAUTH_AUDIENCE
    })
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    conn.request("POST", "/oauth/token", params, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data["access_token"]

async def main():
    bearer_token = get_bearer_token()

    # Create the MCP client
    client = MultiServerMCPClient({
        "math_server": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
            "headers": {
                "Authorization": f"Bearer {bearer_token}"
            }
        }
    })

    # Open a session for that server
    async with client.session("math_server") as session:
        # Load MCP tools from the session
        tools = await load_mcp_tools(session)

        model = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

        # Create LangGraph agent
        agent = create_react_agent(
            model=model,
            tools=tools
        )

        # Ask the agent to use the MCP tool
        result = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Add 7 and 13"}
            ]
        })

        print("Agent Output:", result)

if __name__ == "__main__":
    asyncio.run(main())
