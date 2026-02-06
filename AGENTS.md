# Instructions for Agents

This project implements a Contract Chatbot using LangChain and Streamlit.

## Codebase Rules

1. **No Persistent Storage**: Do not add SQLite or other databases. Keep vector stores in memory.
2. **Modular Design**: Keep ingestion, RAG, and UI separate.
3. **Environment Variables**: Use `config.settings` to access env vars. Do not hardcode API keys.

## Testing
- Run tests using `python -m unittest discover tests`.
- Ensure `PYTHONPATH` includes the root directory.

## MCP Server
- The MCP server is in `mcp_server.py` and uses `fastmcp`.
- It currently indexes `sample_contracts/`.
