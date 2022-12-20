import argparse
import asyncio
import time

import aiofiles
from loguru import logger

from src import gui
from src.authorise import authorise
from src.chat_connector import open_connection
from src.exceptions import InvalidTokenException
from src.listen import listen


async def main():
    parser = argparse.ArgumentParser(description="Client settings")
    parser.add_argument("--host", dest="host", type=str, default="minechat.dvmn.org", help="Host to listen")
    parser.add_argument("--port", dest="port", type=str, default="5000", help="Port")
    parser.add_argument("--token", dest="token", type=str, help="Chat access token")
    parser.add_argument("--username", dest="username", type=str, help="Chat username")
    parser.add_argument("--history", dest="history_path", type=str, default="minechat.history", help="File for message history.")
    args = parser.parse_args()

    args.token = "fbf8e8d0-7bdc-11ed-8c47-0242ac110002"

    loop = asyncio.get_event_loop()

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    history_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    async with aiofiles.open(args.history_path, mode="r") as log_file:
        async for msg in log_file:
            messages_queue.put_nowait(msg)

    try:
        async with open_connection(args.host, 5050) as conn:
            status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
            status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)

            reader, writer = conn
            status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
            try:
                watchdog_queue.put_nowait("Prompt before auth")
                username = await authorise(reader, writer, args.token)
                watchdog_queue.put_nowait("Authorization done")
                status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
                status_updates_queue.put_nowait(gui.NicknameReceived(username))
            except InvalidTokenException:
                status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)
                status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.CLOSED)
                quit()

            await asyncio.gather(
                gui.draw(messages_queue, sending_queue, status_updates_queue),
                read_msgs(args.host, args.port, messages_queue, history_queue, watchdog_queue),
                save_messages(args.history_path, history_queue),
                send_msgs(args.host, args.port, sending_queue, writer, watchdog_queue),
                watch_for_connection(watchdog_queue),
            )

    except RuntimeError:
        logger.error("Exiting...")
        quit()

    loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))


async def send_msgs(host: str, port: int, queue: asyncio.Queue, writer: asyncio.StreamWriter, watchdog_queue: asyncio.Queue):
    while True:
        if not queue.empty():
            msg = queue.get_nowait()
            logger.info(f"User typed {msg}")

            writer.write(f"{msg}\n\n".encode())
            await writer.drain()
            watchdog_queue.put_nowait("Message sent")
        await asyncio.sleep(0)


async def read_msgs(host: str, port: int, queue: asyncio.Queue, history_queue: asyncio.Queue, watchdog_queue: asyncio.Queue):
    try:
        async with open_connection(host, port) as conn:
            reader, _ = conn
            await listen(reader, queue, history_queue, watchdog_queue)
    except RuntimeError:
        logger.error("Exiting...")
        quit()


async def save_messages(filepath: str, queue: asyncio.Queue):
    while True:
        if queue.empty():
            await asyncio.sleep(0)

        async with aiofiles.open(filepath, mode="a") as log_file:
            while not queue.empty():
                msg = queue.get_nowait()
                await log_file.write(msg)


async def watch_for_connection(queue: asyncio.Queue):
    while True:
        if queue.empty():
            await asyncio.sleep(0)

        while not queue.empty():
            msg = queue.get_nowait()
            logger.info(f"[{int(time.time())}] Connection is alive. {msg}")
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
