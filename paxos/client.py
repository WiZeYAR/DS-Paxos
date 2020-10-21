from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node
from .message import PaxosValue, InstanceID, ClientPropose, ClientProposePayload
from numpy import random
from time import sleep
import sys


class Client(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.CLIENT, network)
        self._instance_id: InstanceID = InstanceID(0)

    def request_value(self, value: int):
        """Send a request to all proposers to propose a given value"""
        self._instance_id += 1
        request_message: ClientPropose = ClientPropose(sender=self,
                                                       receiver_role=Role.PROPOSER,
                                                       payload=ClientProposePayload(
                                                           (PaxosValue(value), self._instance_id)
                                                       )
                                                       )
        self.send(Role.PROPOSER, request_message)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of client {self.id}')
        while True:
            for value in sys.stdin:
                self.request_value(value.strip())
