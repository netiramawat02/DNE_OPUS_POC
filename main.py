import argparse
import uvicorn
import os
import sys

def run_server(host="0.0.0.0", port=8000):
    """Runs the FastAPI backend server"""
    print(f"Starting FastAPI Server on {host}:{port}...")
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("api.server:app", host=host, port=port, reload=True)

def run_mcp():
    print("Starting MCP Server...")
    try:
        from mcp_server import mcp
        mcp.run()
    except ImportError as e:
        print(f"Failed to start MCP server: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jules AI Contract Chatbot")
    parser.add_argument("mode", choices=["server", "mcp"], nargs="?", default="server", help="Mode: 'server' (FastAPI Backend) or 'mcp' (MCP Server)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for server")
    parser.add_argument("--port", type=int, default=8000, help="Port for server")

    args = parser.parse_args()

    if args.mode == "server":
        run_server(args.host, args.port)
    elif args.mode == "mcp":
        run_mcp()
