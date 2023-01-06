import asyncio

import aiofiles


async def save_messages(filepath: str, queue: asyncio.Queue):
    while True:
        if queue.empty():
            await asyncio.sleep(0)

        async with aiofiles.open(filepath, mode="a") as log_file:
            while not queue.empty():
                msg = queue.get_nowait()
                await log_file.write(msg)


async def init_history(queue: asyncio.Queue, history_path: str):
    async with aiofiles.open(history_path, mode="r") as log_file:
        async for msg in log_file:
            queue.put_nowait(msg)
