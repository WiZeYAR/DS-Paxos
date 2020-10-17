from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node


class Proposer(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.PROPOSER, network)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of proposer {self.id}')
        while True:
            pass
