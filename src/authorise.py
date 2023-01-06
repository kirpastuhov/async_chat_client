import asyncio
import json

from loguru import logger

from src.exceptions import InvalidTokenException
from src.gui import NicknameReceived, SendingConnectionStateChanged
from src.queues_list import QueueList


async def authorise(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, token: str, queues: QueueList) -> bool:
    queues.watchdog.put_nowait("Prompt before auth")
    data = await reader.readline()
    logger.debug(data.decode())

    writer.write(f"{token}\n".encode())
    await writer.drain()

    data = await reader.readline()
    data = data.decode()

    if not json.loads(data):
        logger.error("Incorrect token. Authorization failed.")
        raise InvalidTokenException

    logger.info(f"Authorization was successful. User: {json.loads(data)['nickname']}")
    queues.watchdog.put_nowait("Authorization done")
    queues.status_updates.put_nowait(SendingConnectionStateChanged.ESTABLISHED)
    queues.status_updates.put_nowait(NicknameReceived(json.loads(data)["nickname"]))
    return True
