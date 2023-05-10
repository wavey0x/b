"""
1. create an app https://my.telegram.org/
2. export API_ID=...
   export API_HASH=...
3. pip install telethon toolz
4. python tg_owner.py
"""
import asyncio
import re
import os

from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat
from toolz import unique


async def main():
    client = TelegramClient(
        "session_name", os.environ["API_ID"], os.environ["API_HASH"]
    )
    await client.start()

    dialogs = await client.get_dialogs()

    owner = [
        f"{x.name} ({x.id})"
        for x in dialogs
        if isinstance(x.entity, (Channel, Chat))
        and re.search(r"yfi|yearn", x.name, re.IGNORECASE)
        and x.entity.creator
    ]
    print("\n".join(unique(owner)))


asyncio.run(main())