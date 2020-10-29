#!/usr/bin/env python3

from typing import NoReturn, Dict
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import Decide, DecidePayload, MessageType, PaxosValue, InstanceID
import pickle

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

        file = open('learner{}_decided_value'.format(self.id), "wb")
        pickle.dump(dict(sorted(self._decided_values.items())), file=file)
        file.close()


    def run(self) -> NoReturn:
        self.log("Start running...")
        while True:
            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)


