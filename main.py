import argparse

import aiofiles
import anyio
from anyio import create_task_group

from src import gui
from src.connection_monitoring import ping_pong, reconnect, watch_for_connection
from src.history import init_history, save_messages
from src.listen import read_msgs
from src.queues_list import QueueList
from src.write import send_msgs


async def main():
    parser = argparse.ArgumentParser(description="Client settings")
    parser.add_argument("--host", dest="host", type=str, default="minechat.dvmn.org", help="Host to listen")
    parser.add_argument("--port", dest="port", type=str, default="5050", help="Port")
    parser.add_argument("--token", dest="token", type=str, help="Chat access token")
    parser.add_argument("--history", dest="history_path", type=str, default="minechat.history", help="File for message history.")
    parser.add_argument("--creds_file", dest="creds_file", type=str, default="creds.txt", help="File for token.")
    args = parser.parse_args()

    queues = QueueList()

    if not args.token:
        async with aiofiles.open(args.creds_file, "r") as f:
            args.token = await f.readline()

    await init_history(queues.messages, args.history_path)

    async with create_task_group() as tg:
        await tg.spawn(gui.draw, queues.messages, queues.sending, queues.status_updates)
        await tg.spawn(save_messages, args.history_path, queues.history)
        await tg.spawn(handle_connection, args.host, 5000, args.port, args.token, queues)


@reconnect
async def handle_connection(host: str, read_port: int, send_port: int, token: str, queues: QueueList):
    async with create_task_group() as tg:
        await tg.spawn(read_msgs, host, read_port, queues)
        await tg.spawn(send_msgs, host, send_port, token, queues)
        await tg.spawn(watch_for_connection, queues.watchdog, queues.status_updates)
        await tg.spawn(ping_pong, queues.sending)


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        pass
    except gui.TkAppClosed:
        pass
