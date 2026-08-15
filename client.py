import argparse
import asyncio
import sys
import threading

import websockets


def read_stdin(loop: asyncio.AbstractEventLoop, commands: asyncio.Queue) -> None:
    for line in sys.stdin:
        command = line.removesuffix("\n").removesuffix("\r")
        try:
            loop.call_soon_threadsafe(commands.put_nowait, command)
        except RuntimeError:
            return

    try:
        loop.call_soon_threadsafe(commands.put_nowait, None)
    except RuntimeError:
        pass


async def send_commands(connection) -> None:
    loop = asyncio.get_running_loop()
    commands = asyncio.Queue()
    threading.Thread(
        target=read_stdin,
        args=(loop, commands),
        daemon=True,
    ).start()

    while (command := await commands.get()) is not None:
        await connection.send(command)


async def display_messages(connection) -> None:
    async for message in connection:
        print(message, flush=True)


async def start_client(address: str) -> None:
    async with websockets.connect(address) as connection:
        sender = asyncio.create_task(send_commands(connection))
        receiver = asyncio.create_task(display_messages(connection))

        done, pending = await asyncio.wait(
            {sender, receiver},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        for task in done:
            task.result()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Connect to the tic-tac-toe server.")
    parser.add_argument("address", help="server WebSocket address, such as ws://localhost:8000")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    asyncio.run(start_client(arguments.address))
