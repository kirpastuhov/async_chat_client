import asyncio

from loguru import logger

from src.queues_list import QueueList


async def send_msgs(writer: asyncio.StreamWriter, queues: QueueList):
    try:
        while True:
            msg = await queues.sending.get()
            logger.info(f"User typed {msg}")

            writer.write(f"{msg}\n\n".encode())
            await writer.drain()
            queues.watchdog.put_nowait("Message sent")
            await asyncio.sleep(0)
    except RuntimeError:
        logger.info("Runtime")
