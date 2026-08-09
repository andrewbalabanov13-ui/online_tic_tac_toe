"""Interactive WebSocket client for online tic-tac-toe."""

import argparse
import asyncio

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed


async def run_client(uri: str) -> None:
    """Connect to the server and exchange terminal messages."""
    try:
        async with connect(uri) as websocket:
            print(await websocket.recv())
            print("Type a message, or 'quit' to disconnect.")

            while True:
                message = await asyncio.to_thread(input, "> ")
                if message.strip().lower() in {"quit", "exit"}:
                    break

                await websocket.send(message)
                print(await websocket.recv())
    except ConnectionRefusedError:
        print(f"Could not connect to {uri}. Is the server running?")
    except ConnectionClosed as error:
        print(f"Connection closed: {error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a tic-tac-toe client.")
    parser.add_argument("--uri", default="ws://127.0.0.1:8000")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run_client(args.uri))
    except KeyboardInterrupt:
        print("\nClient stopped.")


if __name__ == "__main__":
    main()
