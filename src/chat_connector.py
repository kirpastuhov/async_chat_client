import asyncio
import socket
from contextlib import asynccontextmanager

from loguru import logger


@asynccontextmanager
async def open_connection(host: str, port: int):
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        yield reader, writer
    except (OSError, socket.gaierror) as err:
        logger.error(f"Connection error: {err}")
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()
            logger.debug("Closed writer")
