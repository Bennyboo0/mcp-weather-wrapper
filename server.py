import os
import json
from typing import Any, Dict, Optional

import httpx
from fastmcp import FastMCP

API_BASE = os.environ.get("API_BASE", "https://java-api-consumer.onrender.com").rstrip("/")

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")

mcp = FastMCP("weather-advisor-mcp")


async def _get_json(path: str, params: Optional[dict] = None) -> Dict[str, Any]:
    url = f"{API_BASE}{path}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        if "application/json" in ctype:
            return r.json()
        return {"raw": r.text}


# -------------------------
# Your original tools
# -------------------------

@mcp.tool
async def get_weather(city: str, units: str = "imperial") -> Dict[str, Any]:
    """Calls: GET /api/weather?city=...&units=..."""
    return await _get_json("/api/weather", params={"city": city, "units": units})


@mcp.tool
async def health() -> Dict[str, Any]:
    """Calls: GET /health"""
    return await _get_json("/health")


@mcp.tool
async def ping() -> Dict[str, Any]:
    """Simple connectivity test tool for the MCP server."""
    return {"ok": True}


# -------------------------
# ChatGPT Connector-compatible tools
# (required for connectors / deep research)
# -------------------------

@mcp.tool
async def search(query: str) -> Dict[str, Any]:
    """
    Connector-style search tool.
    Treats query as a city name and returns a single result item.
    """
    city = query.strip()
    if not city:
        results = []
    else:
        # We provide a stable "id" that fetch() can use.
        # You can extend this to include units later if you want.
        results = [{
            "id": city,
            "title": f"Weather for {city}",
            "url": f"{API_BASE}/api/weather?city={city}"
        }]

    # Return as a single text content item with JSON-encoded string
    return {
        "content": [{
            "type": "text",
            "text": json.dumps({"results": results})
        }]
    }


@mcp.tool
async def fetch(id: str) -> Dict[str, Any]:
    """
    Connector-style fetch tool.
    Uses id as the city name and returns the full weather payload as text.
    """
    city = (id or "").strip()
    if not city:
        doc = {
            "id": id,
            "title": "Weather",
            "text": "No city provided.",
            "url": API_BASE
        }
    else:
        data = await _get_json("/api/weather", params={"city": city, "units": "imperial"})
        doc = {
            "id": city,
            "title": f"Weather for {city}",
            "text": json.dumps(data, indent=2),
            "url": f"{API_BASE}/api/weather?city={city}"
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(doc)
        }]
    }


if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT, path=MCP_PATH)
