from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.ACCEPTOR, network)

    def run(self) -> NoReturn:
        pass
