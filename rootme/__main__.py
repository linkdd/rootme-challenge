import asyncio

from .client import RootMeClient


client = RootMeClient(
    "irc.root-me.org",
    6667,
    "ddelassus-rootme-challenge",
)

asyncio.run(client.start())
