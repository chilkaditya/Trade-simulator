# main.py

import asyncio
from core.websocket_client import run

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[EXIT] Shutting down simulator.")
