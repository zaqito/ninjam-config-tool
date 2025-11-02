# src/ninjam_config_tool/main.py
import sys
from .app import Application

def run():
    """Application entry point defined in pyproject.toml."""
    try:
        app = Application()
        app.start()
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run()