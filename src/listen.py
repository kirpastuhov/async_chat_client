import asyncio
from asyncio.streams import StreamReader


async def listen(reader: StreamReader, queue: asyncio.Queue, history: asyncio.Queue, watchdog: asyncio.Queue):
    while not reader.at_eof():
        data = await reader.readline()
        msg = data.decode()
        queue.put_nowait(msg)
        history.put_nowait(msg)
        watchdog.put_nowait("New message in chat")
        await asyncio.sleep(0)
