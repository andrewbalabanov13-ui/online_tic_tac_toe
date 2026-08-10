import argparse
import asyncio

import websockets


async def start_client(address: str, name: str) -> None:
    async with websockets.connect(address) as connection:
        await connection.send(f"start_client|{name}")
        async for message in connection:
            print(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Connect to the tic-tac-toe server.")
    parser.add_argument("address", help="server WebSocket address, such as ws://localhost:8000")
    parser.add_argument("name", help="player name sent to the server")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    asyncio.run(start_client(arguments.address, arguments.name))
