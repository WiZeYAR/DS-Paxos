from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node
from .message import PaxosValue, ClientPropose
from numpy import random
from time import sleep


class Client(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.CLIENT, network)

    def request_value(self):
        """Send a request to all proposers to propose a given value"""
        value = random.choice([2, 342, 123, 573, 123, 544])
        request_message: ClientPropose = ClientPropose(sender=self,
                                                       receiver_role=Role.PROPOSER,
                                                       payload=PaxosValue(value)
                                                       )
        self.send(Role.PROPOSER, request_message)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of client {self.id}')
        while True:
            self.request_value()
            sleep(10)
