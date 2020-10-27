from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import Deliver, MessageType, PaxosValue
import sys

class Learner(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.LEARNER, network)
        self._message_callbacks = {
            MessageType.DELIVER: self.deliver
        }
        self._delivered_value: PaxosValue = None

    def deliver(self, deliver_message: Deliver):
        self._delivered_value = deliver_message.payload
        self.log("DECIDED value {0}".format(self._delivered_value))
        sys.stdout.flush()

    def run(self) -> NoReturn:
        self.log("Start running")
        while True:
            message: MessageT = self.listen()
            if message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
