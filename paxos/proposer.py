from typing import NoReturn, List
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue, ClientPropose
from .message import PreparePayload, Prepare, Propose, ProposePayload
from .message import Promise, PromisePayload, Accept, AcceptPayload, Deliver

# Naive solution to guarantee uniqueness of round ID between multiple proposers
primes = [2, 3, 5, 7, 11, 13, 17]


class Proposer(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.PROPOSER, network)
        # The ID of the round currently initiated by the proposer
        self._round_id: RoundID = RoundID(1)
        # The value to be proposed in the next PROPOSE phase
        self._propose_next_value = None
        # The value that the proposer will try to propose if unconstrained
        self._desired_value = None
        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.CLIENT_PROPOSE: self.prepare_phase,
            MessageType.PROMISE: self.propose_phase,
            MessageType.ACCEPT: self.accept_phase
        }
        self._majority = 2
        # Promises received from acceptors corresponding to the current round
        self._promises_received = 0
        # Accepted value and round in which it was accepted of the latest accepted value among the received promises
        self._latest_promise: List[RoundID, PaxosValue] = [RoundID(0), None]
        # Accept messages received from acceptors associated to this round
        self._accept_messages_current_round = 0

    def prepare_phase(self, client_message: ClientPropose) -> None:
        self._desired_value = client_message.payload

        # Reset round variables
        self._propose_next_value = None
        self._promises_received = 0
        self._latest_promise: List[RoundID, PaxosValue] = [RoundID(0), None]
        self._accept_messages_current_round = 0

        # Start new round
        self._round_id *= primes[self.id]
        prepare_message = Prepare(sender=self,
                                  receiver_role=Role.ACCEPTOR,
                                  payload=PreparePayload((self._round_id,))
                                  )
        self.send(Role.ACCEPTOR, prepare_message)
        print("Started new round with ID {0}, with desired value to propose {1}"
              .format(self._round_id, self._desired_value)
              )

    def propose_phase(self, promise_message: Promise) -> None:
        payload: PromisePayload = promise_message.payload
        acceptor_round: RoundID = payload[0]
        round_accepted: RoundID = payload[1]
        value_accepted: PaxosValue = payload[2]

        if acceptor_round == self._round_id:
            self._promises_received += 1
            if round_accepted > self._latest_promise[0]:
                self._latest_promise[0] = round_accepted
                self._latest_promise[1] = value_accepted

        if self._promises_received == self._majority:
            # Set value to propose next to the value received accepted in the highest round, if any, otherwise use
            # value requested by the clint
            if self._latest_promise[0] == 0:
                self._propose_next_value = self._desired_value
            else:
                self._propose_next_value = self._latest_promise[1]

            # Send Propose to acceptors
            propose_message = Propose(sender=self,
                                      receiver_role=Role.ACCEPTOR,
                                      payload=ProposePayload((self._round_id, self._propose_next_value))
                                      )
            self.send(Role.ACCEPTOR, message=propose_message)
            print("Proposing value {0}".format(self._propose_next_value))

    def accept_phase(self, accept_message: Accept):
        payload: AcceptPayload = accept_message.payload
        if payload[0] == self._round_id:
            self._accept_messages_current_round += 1
        # If a majority of acceptor accepted the same value in this round, then decide it
        if self._accept_messages_current_round == self._majority:
            deliver_message: Deliver = Deliver(sender=self,
                                               receiver_role=Role.LEARNER,
                                               payload=payload[1])
            self.send(Role.LEARNER, deliver_message)


    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of proposer {self.id}')

        while True:
            message: MessageT = self.listen()
            if message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
