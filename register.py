import argparse
import asyncio
import json
import tkinter as tk
from tkinter import messagebox

import aiofiles
from loguru import logger

from src.chat_connector import open_connection


async def register(host: str, port: int, root: tk.Tk, entry: tk.Entry, creds_file: str):
    username = entry.get().strip()

    if not username:
        messagebox.showerror("Error", "Empty username field, please try again.")
        return

    entry.delete(0, tk.END)
    try:
        async with open_connection(host, port) as conn:
            reader, writer = conn

            await reader.readline()

            writer.write("\n".encode())
            await writer.drain()

            await reader.readline()

            writer.write(f"{username}\n".encode())
            await writer.drain()

            response = await reader.readline()
            response = response.decode()
            access_token = json.loads(response)["account_hash"]

            async with aiofiles.open(creds_file, "w") as f:
                await f.write(access_token)
                logger.info(f"Saved token into {creds_file}")

            messagebox.showinfo("", f"User '{username}' was registered!")
            root.destroy()

    finally:
        writer.close()
        await writer.wait_closed()


def main():
    parser = argparse.ArgumentParser(description="Client settings")
    parser.add_argument("--host", dest="host", type=str, default="minechat.dvmn.org", help="Host to listen")
    parser.add_argument("--port", dest="port", type=str, default="5050", help="Port")
    parser.add_argument("--creds_file", dest="creds_file", type=str, default="creds.txt", help="File for token.")
    args = parser.parse_args()

    root = tk.Tk()
    root.title("Minecraft Chat")

    label = tk.Label(text="Register new user")
    label.pack()

    entry = tk.Entry(width=50)
    entry.pack()

    button = tk.Button(text="Submit")
    button.config(command=lambda: asyncio.run(register(args.host, args.port, root, entry, args.creds_file)))
    button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
