import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        tools = await client.list_tools()
        print("TOOLS:", [t.name for t in tools])

        # call ping tool if it exists
        if any(t.name == "ping" for t in tools):
            result = await client.call_tool("ping", {})
            print("PING RESULT:", result)

asyncio.run(main())
