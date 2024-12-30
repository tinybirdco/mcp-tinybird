import sys
from .run_sse import main as run_sse
from .run_stdio import main as run_stdio

def main():
    # If no arguments provided, default to stdio mode
    if len(sys.argv) == 1:
        run_stdio()
        return

    mode = sys.argv[1]
    if mode == "sse":
        run_sse()
    elif mode == "stdio":
        run_stdio()
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: sse, stdio (default)")
        sys.exit(1)

if __name__ == "__main__":
    main() 