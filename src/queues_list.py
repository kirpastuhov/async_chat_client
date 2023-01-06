import asyncio
from dataclasses import dataclass, field


@dataclass
class QueueList:
    messages: asyncio.Queue = field(default=asyncio.Queue())
    sending: asyncio.Queue = field(default=asyncio.Queue())
    status_updates: asyncio.Queue = field(default=asyncio.Queue())
    history: asyncio.Queue = field(default=asyncio.Queue())
    watchdog: asyncio.Queue = field(default=asyncio.Queue())
