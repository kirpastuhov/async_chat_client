import asyncio

from src import gui
from src.chat_connector import open_connection
from src.queues_list import QueueList


async def read_msgs(host: str, port: int, queues: QueueList):
    async with open_connection(host, port) as conn:
        reader, _ = conn
        if not reader:
            raise ConnectionError("Can't establish reader connection.")
        queues.status_updates.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
        while True:
            data = await reader.readline()
            msg = data.decode()
            queues.messages.put_nowait(msg)
            queues.history.put_nowait(msg)
            queues.watchdog.put_nowait("New message in chat")
            await asyncio.sleep(0)
