"""WebSocket server for online tic-tac-toe."""

import argparse
import asyncio

from websockets.asyncio.server import ServerConnection, serve


async def handle_client(websocket: ServerConnection) -> None:
    """Receive messages from one client and echo them back."""
    address = websocket.remote_address
    print(f"Client connected: {address}")
    await websocket.send("Connected to the tic-tac-toe server.")

    try:
        async for message in websocket:
            print(f"Received from {address}: {message}")
            await websocket.send(f"Server received: {message}")
    finally:
        print(f"Client disconnected: {address}")


async def run_server(host: str, port: int) -> None:
    """Run the server until it is interrupted."""
    async with serve(handle_client, host, port):
        print(f"Server listening on ws://{host}:{port}")
        await asyncio.get_running_loop().create_future()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the tic-tac-toe server.")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="IPv4 address to bind to (default: all IPv4 interfaces)",
    )
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run_server(args.host, args.port))
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
