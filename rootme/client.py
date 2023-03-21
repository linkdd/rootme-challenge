from enum import Enum, auto
import codecs

from .protocol import Client

class RootMeState(Enum):
    CONNECTING = auto()
    WAIT_FOR_MESSAGE = auto()
    WAIT_FOR_REPLY = auto()


class RootMeClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._state = RootMeState.CONNECTING

    async def on_connect(self):
        self._state = RootMeState.WAIT_FOR_MESSAGE
        print("Starting challenge with Candy")
        await self.message("Candy", "!ep3")

    async def on_message(self, target: str, source: str | None, message: str):
        match self._state:
            case RootMeState.WAIT_FOR_MESSAGE:
                if source == "Candy":
                    self._state = RootMeState.WAIT_FOR_REPLY
                    print("Received encoded message from Candy:", message)
                    decoded = codecs.decode(message, "rot_13")
                    print("Sending response:", decoded)
                    await self.message("candy", f"!ep3 -rep {decoded}")

            case RootMeState.WAIT_FOR_REPLY:
                if source == "Candy":
                    print("Received reply from Candy:", message)
                    print("Exiting...")
                    self.stop()
