from typing import Optional

from dataclasses import dataclass
import asyncio
import re


@dataclass
class Message:
    prefix: Optional[str]
    command: str
    params: list[str]

    @property
    def nick(self):
        if self.prefix is not None:
            return self.prefix.split("!")[0]

        return None

    @staticmethod
    def from_line(line: str) -> "Message":
        prefix = None
        if line.startswith(":"):
            prefix, line = line[1:].split(" ", 1)

        parts = line.split(" ")
        command = parts.pop(0)
        params = []

        while len(parts) > 0:
            part = parts.pop(0)

            if part.startswith(":"):
                params.append(" ".join([part[1:]] + parts))
                break

            params.append(part)

        return Message(prefix, command, params)


class Client:
    def __init__(self, host: str, port: int, nick: str):
        self.host = host
        self.port = port
        self.nick = nick

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._running = False

    async def start(self):
        self._running = True
        self._reader, self._writer = await asyncio.open_connection(
            self.host,
            self.port,
        )

        print(f"Connected to {self.host}:{self.port}")

        self._writer.write(f"NICK {self.nick}\r\n".encode())
        self._writer.write(f"USER {self.nick} 0 * :{self.nick}\r\n".encode())
        await self._writer.drain()

        while self._running:
            line = await self._reader.readline()
            if not line:
                break

            line = line.decode().strip()
            message = Message.from_line(line)

            match message.command:
                case "PING":
                    await self.pong(message)

                case "001":
                    await self.on_connect()

                case "PRIVMSG":
                    target = message.params[0]
                    source = message.nick
                    message = message.params[1]

                    await self.on_message(target, source, message)

                case _:
                    """print(f"Unhandled message: {message}")"""

        self._writer.close()
        await self._writer.wait_closed()
        self._reader = self._writer = None

    async def on_connect(self):
        pass

    async def on_message(self, target: str, source: str | None, message: str):
        pass

    async def join(self, channel: str):
        self._writer.write(f"JOIN {channel}\r\n".encode())
        await self._writer.drain()

    async def message(self, target: str, content: str):
        self._writer.write(f"PRIVMSG {target} :{content}\r\n".encode())
        await self._writer.drain()

    async def pong(self, message: Message):
        self._writer.write(f"PONG {message.params[0]}]r]n".encode())
        await self._writer.drain()

    def stop(self):
        self._running = False
