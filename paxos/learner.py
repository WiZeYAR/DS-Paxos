from typing import NoReturn, Dict
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import Decide, DecidePayload, MessageType, PaxosValue, InstanceID
import sys

class Learner(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.LEARNER, network)
        self._message_callbacks = {
            MessageType.DECIDE: self.decide
        }
        self._decided_values: Dict[InstanceID, PaxosValue] = {}

    def decide(self, deliver_message: Decide):
        payload: DecidePayload = deliver_message.payload
        decided_value: PaxosValue = payload[0]
        instance: InstanceID = payload[1]

        self._decided_values[instance] = decided_value
        self.log("DECIDED value {0} for instance {1}".format(self._decided_values[instance], instance))
        print("DECIDED value {0} for instance {1}".format(self._decided_values[instance], instance))
        sys.stdout.flush()

    def run(self) -> NoReturn:
        self.log("Start running...")
        while True:
            message: MessageT = self.listen()
            if message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
