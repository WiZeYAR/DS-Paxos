from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node, Message, SeqID, PaxosID, Payload
import time

class Proposer(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.PROPOSER, network)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of proposer {self.id}')
        round = 0
        while True:
            round += 1
            message = Message(sender=self,
                              receiver_role=Role.ACCEPTOR,
                              payload=Payload( (SeqID(round), PaxosID(round), "Hello!"))
                              )
            self.send(0, message)
            print("Sent message for round {}".format(round))
            time.sleep(5)