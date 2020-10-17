from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node
from .message import RoundID, PaxosValue
from .message import PreparePayload, Prepare, PromisePayload, Promise


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.ACCEPTOR, network)
        # Latest round the acceptor has participated in
        self.latest_round_ID: RoundID = RoundID(0)
        # Accepted value, if any
        self.accepted_value: PaxosValue = PaxosValue(0)
        # Round in which the accepted value was accepted
        self.accepted_round_ID: RoundID = RoundID(0)
        self.accepted_value_yet: bool = False

    def promise(self):
        prepare_message: Prepare = self.listen()
        payload: PreparePayload = prepare_message.payload
        round_ID: RoundID = payload[0]
        if round_ID > self.latest_round_ID:
            self.latest_round_ID = round_ID
            promise_message: Promise = Promise(sender=self,
                                               receiver_role=Role.PROPOSER,
                                               payload=PromisePayload((self.latest_round_ID,
                                                                       self.accepted_round_ID,
                                                                       self.accepted_value))
                                               )
            self.send(group=Role.PROPOSER, message=promise_message)
            print("Sending Promise for round ID: {}".format(self.latest_round_ID))

    def accept(self):
        pass


    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of acceptor {self.id}')

        while True:
            self.promise()
            self.accept()

