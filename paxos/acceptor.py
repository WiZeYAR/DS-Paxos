from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue
from .message import PreparePayload, Prepare, PromisePayload, Promise, ProposePayload, Propose, AcceptPayload, Accept, Message


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.ACCEPTOR, network)
        # Latest round the acceptor has participated in
        self._latest_round_ID: RoundID = RoundID(0)
        # Accepted value, if any
        self._accepted_value: PaxosValue = PaxosValue(0)
        # Round in which the accepted value was accepted
        self._accepted_round_ID: RoundID = RoundID(0)
        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.PREPARE: self.promise,
            MessageType.PROPOSE: self.accept
        }

    def promise(self, prepare_message: Prepare):
        payload: PreparePayload = prepare_message.payload
        round_ID: RoundID = payload[0]
        if round_ID > self._latest_round_ID:
            self._latest_round_ID = round_ID
            promise_message: Promise = Promise(sender=self,
                                               receiver_role=Role.PROPOSER,
                                               payload=PromisePayload((self._latest_round_ID,
                                                                       self._accepted_round_ID,
                                                                       self._accepted_value))
                                               )
            self.send(group=Role.PROPOSER, message=promise_message)
            print("Sending Promise for round ID: {}".format(self._latest_round_ID))

    def accept(self, propose_message: Propose):
        payload: ProposePayload = propose_message.payload
        if payload[0] >= self._latest_round_ID:
            if self._accepted_value != payload[1]:
                print("Acceptor {0} accepted new value {1} for round {2}"
                      .format(self.id, payload[1], payload[0])
                      )
            self._accepted_value = payload[1]
            self._accepted_round_ID = payload[0]
            accept_message: Accept = Accept(sender=self,
                                            receiver_role=Role.PROPOSER,
                                            payload=AcceptPayload((self._accepted_round_ID, self._accepted_value))
                                            )
            self.send(Role.PROPOSER, accept_message)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of acceptor {self.id}')

        while True:
            message: MessageT = self.listen()
            if message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
