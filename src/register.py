import asyncio
import json

from loguru import logger

from src.chat_connector import open_connection


async def register(host: str, port: int, status_updates, username_queue: asyncio.Queue, register_queue):
    async with open_connection(host, port) as conn:
        reader, writer = conn
        data = await reader.readline()
        logger.debug(data.decode())

        writer.write("\n".encode())
        await writer.drain()

        data = await reader.readline()
        logger.debug(data.decode())

        username = await username_queue.get()
        writer.write(f"{username}\n".encode())
        await writer.drain()

        data = await reader.readline()
        data = json.loads(data.decode())
        logger.debug(data)
        with open("creds.txt", "w") as f:
            f.write(data["account_hash"])
            register_queue.put_nowait("creds.txt")

        return data
