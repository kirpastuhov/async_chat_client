import json
from asyncio import StreamReader, StreamWriter

from loguru import logger

from src.exceptions import InvalidTokenException


async def authorise(reader: StreamReader, writer: StreamWriter, token: str) -> str:
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
    return json.loads(data)["nickname"]
