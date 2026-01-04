# MCP Weather Wrapper

This project implements a Model Context Protocol (MCP) server that wraps an
existing Weather API (Assignment 2) and exposes its endpoints as tools usable
inside the ChatGPT desktop application.

## Tools

- `get_weather(city, units)`
  - Calls: `GET /api/weather?city=...&units=...`
- `health()`
  - Calls: `GET /health`

## Local Run

```bash
pip install -r requirements.txt
export API_BASE=https://java-api-consumer.onrender.com
python server.py
