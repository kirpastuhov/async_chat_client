import asyncio

from loguru import logger

from src.authorise import authorise
from src.chat_connector import open_connection
from src.queues_list import QueueList


async def send_msgs(host: str, port: int, token: str, queues: QueueList):
    try:
        async with open_connection(host, port) as conn:
            reader, writer = conn

            await authorise(reader, writer, token, queues)

            while True:
                msg = await queues.sending.get()
                logger.info(f"User typed {msg}")

                writer.write(f"{msg}\n\n".encode())
                await writer.drain()
                queues.watchdog.put_nowait("Message sent")
                await asyncio.sleep(0)
    except RuntimeError:
        logger.info("Runtime")
