import os
import json
import http.client
import urllib.parse
import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()

OAUTH_DOMAIN = os.getenv("OAUTH_DOMAIN")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MCP_URL = "http://127.0.0.1:8000/mcp"



# Define connection and endpoint
conn = http.client.HTTPSConnection("smruti-ai-solution.us.auth0.com")

# Prepare form-encoded data
params = urllib.parse.urlencode({
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'audience': OAUTH_AUDIENCE
})
# Set headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
# Make the POST request
conn.request("POST", "/oauth/token", params, headers)
# Get the response
res = conn.getresponse()
bearer_token = res.read().decode("utf-8")


async def main():
    transport = StreamableHttpTransport(
        url=MCP_URL,
        headers={
            "Authorization": f"Bearer {bearer_token}"
        }
    )

    async with Client(transport) as client:
        resp = await client.call_tool(
            "add",
            {"a": 3, "b": 5}
        )
        first_cb_text = None
        for cb in resp.content:
            first_cb_text = getattr(cb, "text", None)
            if first_cb_text:
                break
        if not first_cb_text:
            print("No extraction content found.")
            return

        extracted_json = json.loads(first_cb_text)
        print("Tool result:", extracted_json)

if __name__ == "__main__":
    asyncio.run(main())


