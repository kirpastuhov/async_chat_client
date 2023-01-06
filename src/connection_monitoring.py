import asyncio
import socket
import time

import anyio
from async_timeout import timeout
from loguru import logger

from src import gui

ATTEMPT_DELAY_SECS = 3
ATTEMPTS_BEFORE_DELAY = 2
PING_PONG_DELAY = 5


def reconnect(func):
    async def wrapper(*args, **kwargs):
        attempt = 0
        while True:
            try:
                await func(*args, **kwargs)
            except ConnectionError as e:
                logger.error(f"Get connection error: {e}")
                continue
            except (ConnectionRefusedError, ConnectionResetError, TimeoutError, socket.gaierror, RuntimeError) as e:
                if attempt >= 10:
                    logger.debug(f"No connections. Retry in {ATTEMPT_DELAY_SECS} seconds.")
                    await anyio.sleep(ATTEMPT_DELAY_SECS)
                    continue
                attempt += 1
                logger.debug(f"No connection. Trying to connect again.")

    return wrapper


async def ping_pong(queue: asyncio.Queue):
    while True:
        queue.put_nowait("")
        await anyio.sleep(PING_PONG_DELAY)


async def watch_for_connection(queue: asyncio.Queue, status_updates: asyncio.Queue):
    timeout_seconds = 3
    while True:
        try:
            async with timeout(timeout_seconds) as cm:
                message = await queue.get()
                logger.info(f"[{int(time.time())}] Connection is alive. {message}")
        except (asyncio.exceptions.TimeoutError,) as e:
            if not cm.expired:
                raise e
            message = f"{timeout_seconds}s timeout is elapsed"
            logger.warning(message)
            status_updates.put_nowait(gui.ReadConnectionStateChanged.CLOSED)
            status_updates.put_nowait(gui.SendingConnectionStateChanged.CLOSED)
            raise ConnectionError(message)
