import os
from typing import Any, Dict, Optional

import httpx
from fastmcp import FastMCP

# Your Assignment 2 API base URL (Render app)
API_BASE = os.environ.get(
    "API_BASE",
    "https://java-api-consumer.onrender.com"
).rstrip("/")

# MCP server settings
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")

mcp = FastMCP("weather-advisor-mcp")

from starlette.responses import JSONResponse
from starlette.requests import Request

@mcp.route("/")
async def root(_: Request):
    return JSONResponse({
        "status": "ok",
        "message": "MCP Weather Wrapper is running",
        "mcp_endpoint": MCP_PATH
    })

@mcp.route("/ping")
async def ping(_: Request):
    return JSONResponse({"ok": True})


async def _get_json(path: str, params: Optional[dict] = None) -> Dict[str, Any]:
    url = f"{API_BASE}{path}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        if "application/json" in ctype:
            return r.json()
        return {"raw": r.text}


@mcp.tool
async def get_weather(city: str, units: str = "imperial") -> Dict[str, Any]:
    """
    Calls your Assignment 2 endpoint:
      GET /api/weather?city=...&units=...

    Args:
      city: City name (e.g., "Boston", "Jerusalem")
      units: "imperial" or "metric"
    """
    return await _get_json(
        "/api/weather",
        params={"city": city, "units": units},
    )


@mcp.tool
async def health() -> Dict[str, Any]:
    """
    Calls your Assignment 2 health endpoint:
      GET /health
    """
    return await _get_json("/health")


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=HOST,
        port=PORT,
        path=MCP_PATH,
    )
