from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node
from .message import RoundID, PaxosValue
from .message import PreparePayload, Prepare, Propose
import time

# Naive solution to guarantee uniqueness of round ID between multiple proposers
primes = [2,3,5,7,11,13,17]

class Proposer(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.PROPOSER, network)
        # The ID of the round currently initiated by the proposer
        self._round_id: RoundID = RoundID(1)
        # The value to be proposed in the next PROPOSE phase
        self._propose_next_value = PaxosValue(0)
        # The value that the proposer will try to propose if unconstrained
        self._desired_value = self.id

    def prepare_phase(self) -> None:
        self._round_id *= primes[self.id]
        prepare_message = Prepare(sender=self,
                                  receiver_role=Role.ACCEPTOR,
                                  payload=PreparePayload((self._round_id,))
                                  )
        self.send(Role.ACCEPTOR, prepare_message)

    def propose_phase(self) -> None:
        time.sleep(10)

    def run(self) -> NoReturn:
        print(f'Entering paxos in a role of proposer {self.id}')

        while True:
            self.prepare_phase()
            self.propose_phase()
