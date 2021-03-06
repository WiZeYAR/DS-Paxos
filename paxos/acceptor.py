from typing import NoReturn, Dict, List
import time

from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue, InstanceID
from .message import PreparePayload, Prepare, PromisePayload, Promise, ProposePayload, Propose, AcceptPayload, Accept, Message


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network, plr: float, lifetime: float) -> None:
        super().__init__(id, Role.ACCEPTOR, network, plr, lifetime)
        self._started_instances: List[InstanceID] = []
        # Latest round the acceptor has participated in for each instance
        self._latest_round_ID: Dict[InstanceID, RoundID] = {}
        # Accepted value, if any, for each started instance
        self._accepted_value: Dict[InstanceID, PaxosValue] = {}
        # Round in which the accepted value was accepted for each started instance
        self._accepted_round_ID: Dict[InstanceID, RoundID] = {}

        self._preprepared_promise = False
        self._preprepared_promise_round: RoundID = None


        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.PREPARE: self.promise_parallel,
            MessageType.PROPOSE: self.accept_parallel
        }


    def promise_parallel(self, prepare_message: Prepare):
        payload: PreparePayload = prepare_message.payload
        round_id: RoundID = payload[0]
        instance: InstanceID = payload[1]
        preprepare: bool = payload[2]
        self._preprepared_promise = preprepare


        # If this instance is new add it to the list of started instances
        if instance not in self._started_instances:
            self._started_instances.append(instance)
            self._latest_round_ID[instance] = RoundID(0)
            self._accepted_value[instance] = None
            self._accepted_round_ID[instance] = RoundID(0)

        if round_id > self._latest_round_ID[instance]:
            self._latest_round_ID[instance] = round_id

            promise_message: Promise = Promise(sender=self,
                                               receiver_role=Role.PROPOSER,
                                               payload=PromisePayload((self._latest_round_ID[instance],
                                                                       self._accepted_round_ID[instance],
                                                                       self._accepted_value[instance],
                                                                       instance))
                                               )
            self.send(message=promise_message)
            self.log_debug("Sending Promise for round {0} and instance {1}"
                     .format(self._latest_round_ID[instance], instance)
                     )

        if preprepare:
            self._preprepared_promise_round = round_id

    def accept_parallel(self, propose_message: Propose):
        payload: ProposePayload = propose_message.payload
        round_id: RoundID = payload[0]
        proposed_value: PaxosValue = payload[1]
        instance: InstanceID = payload[2]
        preprepared_promise = payload[3]

        if preprepared_promise and self._preprepared_promise and instance not in self._started_instances:
            self._started_instances.append(instance)
            self._latest_round_ID[instance] = self._preprepared_promise_round
            self._accepted_value[instance] = None
            self._accepted_round_ID[instance] = RoundID(0)

        # Not received a promise for this instance yet, ignore
        if instance not in self._started_instances:
            return

        if round_id >= self._latest_round_ID[instance]:
            if self._accepted_value[instance] is not proposed_value:
                self.log_debug("Accepted value {0} for round {1} and instance {2}"
                         .format(proposed_value, round_id, instance)
                         )

            self._accepted_value[instance] = proposed_value
            self._accepted_round_ID[instance] = round_id
            accept_message_proposers: Accept = Accept(sender=self,
                                            receiver_role=Role.PROPOSER,
                                            payload=AcceptPayload(
                                                (self._accepted_round_ID[instance],
                                                 self._accepted_value[instance],
                                                 instance))
                                            )
            self.send(accept_message_proposers)

            accept_message_learners: Accept = Accept(sender=self,
                                                      receiver_role=Role.LEARNER,
                                                      payload=AcceptPayload(
                                                          (self._accepted_round_ID[instance],
                                                           self._accepted_value[instance],
                                                           instance))
                                                      )
            self.send(accept_message_learners)


    def run(self) -> NoReturn:
        self.log_info("Start running...")
        start = time.time()

        while True:
            if self.lifetime > 0.0:
                if time.time()-start > self.lifetime:
                    self.log_warning("Terminating...")
                    break

            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
