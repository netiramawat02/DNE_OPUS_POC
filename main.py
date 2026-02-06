import argparse
import subprocess
import sys
import os

def run_ui():
    print("Starting UI...")
    # Ensure we are in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)

    try:
        subprocess.run(["streamlit", "run", "ui/app.py"], check=True)
    except KeyboardInterrupt:
        print("\nUI stopped.")

def run_mcp():
    print("Starting MCP Server...")
    # Import here to avoid early initialization if just running UI
    try:
        from mcp_server import mcp
        mcp.run()
    except ImportError as e:
        print(f"Failed to start MCP server: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jules AI Contract Chatbot")
    parser.add_argument("mode", choices=["ui", "mcp"], nargs="?", default="ui", help="Mode to run: 'ui' (Streamlit) or 'mcp' (MCP Server)")

    args = parser.parse_args()

    if args.mode == "ui":
        run_ui()
    elif args.mode == "mcp":
        run_mcp()
