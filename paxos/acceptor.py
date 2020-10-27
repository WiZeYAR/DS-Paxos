from typing import NoReturn, Dict, List
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue, InstanceID
from .message import PreparePayload, Prepare, PromisePayload, Promise, ProposePayload, Propose, AcceptPayload, Accept, Message


class Acceptor(Node):
    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.ACCEPTOR, network)
        self._started_instances: List[InstanceID] = []
        # Latest round the acceptor has participated in for each instance
        self._latest_round_ID: Dict[InstanceID, RoundID] = {}
        # Accepted value, if any, for each started instance
        self._accepted_value: Dict[InstanceID, PaxosValue] = {}
        # Round in which the accepted value was accepted for each started instance
        self._accepted_round_ID: Dict[InstanceID, RoundID] = {}


        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.PREPARE: self.promise_parallel,
            MessageType.PROPOSE: self.accept_parallel
        }


    def promise_parallel(self, prepare_message: Prepare):
        payload: PreparePayload = prepare_message.payload
        round_id: RoundID = payload[0]
        instance: InstanceID = payload[1]

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
            self.log("Sending Promise for round {0} and instance {1}"
                     .format(self._latest_round_ID[instance], instance)
                     )

    def accept_parallel(self, propose_message: Propose):
        payload: ProposePayload = propose_message.payload
        round_id: RoundID = payload[0]
        proposed_value: PaxosValue = payload[1]
        instance: InstanceID = payload[2]

        if round_id >= self._latest_round_ID[instance]:
            if self._accepted_value[instance] is not proposed_value:
                self.log("Accepted value {0} for round {1} and instance {2}"
                         .format(proposed_value, round_id, instance)
                         )

            self._accepted_value[instance] = proposed_value
            self._accepted_round_ID[instance] = round_id
            accept_message: Accept = Accept(sender=self,
                                            receiver_role=Role.PROPOSER,
                                            payload=AcceptPayload(
                                                (self._accepted_round_ID[instance],
                                                 self._accepted_value[instance],
                                                 instance))
                                            )
            self.send(accept_message)


    def promise(self, prepare_message: Prepare):
        payload: PreparePayload = prepare_message.payload
        round_ID: RoundID = payload[0]
        instance_id: InstanceID = payload[1]
        if instance_id > self._instance_id:
            self._instance_id = instance_id
            self._latest_round_ID = RoundID(0)
            self._accepted_value: PaxosValue = PaxosValue(0)
            self._accepted_round_ID: RoundID = RoundID(0)

        if round_ID > self._latest_round_ID:
            self._latest_round_ID = round_ID
            promise_message: Promise = Promise(sender=self,
                                               receiver_role=Role.PROPOSER,
                                               payload=PromisePayload((self._latest_round_ID,
                                                                       self._accepted_round_ID,
                                                                       self._accepted_value,
                                                                       self._instance_id))
                                               )
            self.send(message=promise_message)
            self.log("Sending Promise for round {0} and instance {1}".format(self._latest_round_ID, self._instance_id))

    def accept(self, propose_message: Propose):
        payload: ProposePayload = propose_message.payload
        instance_id: InstanceID = payload[2]

        if payload[0] >= self._latest_round_ID:
            if self._accepted_value != payload[1]:
                self.log("Accepted value {0} for round {1} and instance {2}"
                      .format(payload[1], payload[0], instance_id)
                      )
            self._accepted_value = payload[1]
            self._accepted_round_ID = payload[0]
            accept_message: Accept = Accept(sender=self,
                                            receiver_role=Role.PROPOSER,
                                            payload=AcceptPayload((self._accepted_round_ID, self._accepted_value, instance_id))
                                            )
            self.send(accept_message)

    def run(self) -> NoReturn:
        self.log("Start running...")

        while True:
            message: MessageT = self.listen()
            if message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)
