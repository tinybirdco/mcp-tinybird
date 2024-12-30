import sys
from .run_sse import main as run_sse
from .run_stdio import main as run_stdio

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m mcp_tinybird [sse|stdio]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "sse":
        run_sse()
    elif mode == "stdio":
        run_stdio()
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: sse")  # Add stdio when implemented
        sys.exit(1)

if __name__ == "__main__":
    main() 