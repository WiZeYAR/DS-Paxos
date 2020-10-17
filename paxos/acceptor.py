from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node
from .node import NodeID, Node, Message, SeqID, PaxosID, Payload


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.ACCEPTOR, network)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of acceptor {self.id}')
        while True:
            message: Message = self.listen()
            msg_sender = message.sender_id
            msg_round = message.payload[0]
            msg_text = message.payload[2]
            print("Received message from acceptor {0} for round {1} with text: {2} "
                  .format(msg_sender, msg_round, msg_text)
                  )
