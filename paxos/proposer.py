from typing import NoReturn, List, Dict
import time

from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue, InstanceID, ClientPropose, ClientProposePayload
from .message import PreparePayload, Prepare, Propose, ProposePayload
from .message import Promise, PromisePayload, Accept, AcceptPayload, Decide, DecidePayload
from .message import RequestAck



class Proposer(Node):
    # Naive solution to guarantee uniqueness of round ID between multiple proposers
    primes = [2, 3, 5, 7, 11, 13, 17]
    BASE_TIMEOUT = 0.33
    TIMEOUT_GROWTH_FACTOR = 1.1

    def __init__(self, id: NodeID, network: Network) -> None:
        super().__init__(id, Role.PROPOSER, network)
        # The ID of the round currently initiated by the proposer for each undecided instance
        self._round_id: Dict[InstanceID, RoundID] = {}
        # The values to be proposed in the next PROPOSE phase of each undecided instance
        self._value_to_propose: Dict[InstanceID, PaxosValue] = {}
        # Promises received from acceptors corresponding to the current round for each undecided instance
        self._promises_received: Dict[InstanceID, int] = {}
        # Accepted value and round in which it was accepted of the latest accepted value among the received promises
        # for each instance
        self._latest_promise: Dict[InstanceID, List[RoundID, PaxosValue]] = {}
        # Accept messages received from acceptors associated to this round
        self._accept_messages_current_round: Dict[InstanceID, int] = {}

        # Keep track of which value has been request by a client for each instance and the list of decided instances
        self._undecided_instances: List[InstanceID] = []
        self._client_requests: Dict[InstanceID, PaxosValue] = {}
        self._decided_values: Dict[InstanceID, PaxosValue] = {}

        # The timeout defines for each instance the maximum time (in sec) that a round can take; if exceeded the
        # proposer starts a new round with higher timeout
        self._round_timeouts: Dict[InstanceID, float] = {}
        self._last_prepare_time: Dict[InstanceID, float] = {}

        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.CLIENT_PROPOSE: self.client_request_callback,
            MessageType.PROMISE: self.propose_phase_parallel,
            MessageType.ACCEPT: self.accept_phase_parallel
        }

    def client_request_callback(self, client_request: ClientPropose):
        payload: ClientProposePayload = client_request.payload
        value: PaxosValue = payload[0]
        instance: InstanceID = payload[1]

        # Send an ACK to the clients confirming a request for the current instance has been received
        ack_message: RequestAck = RequestAck(sender=self,
                                             receiver_role=Role.CLIENT,
                                             payload=instance)
        self.send(ack_message)


        # If a request is received for a new instance, add the instance to the list of undecided ones
        # and save the corresponding value to propose then initialize new instance
        if instance not in self._client_requests:
            self._client_requests[instance] = value
            self._undecided_instances.append(instance)

            self._round_id[instance] = RoundID(1)
            self._value_to_propose[instance] = None
            self._promises_received[instance] = 0
            self._latest_promise[instance] = [RoundID(0), None]
            self._round_timeouts[instance] = Proposer.BASE_TIMEOUT

            self._accept_messages_current_round[instance] = 0

            self.prepare_phase_parallel(instance)

    def first_undecided_instance(self) -> InstanceID:
        self._undecided_instances.sort()
        return self._undecided_instances[0]

    def prepare_phase_parallel(self, instance: InstanceID) -> None:
        # Start new round
        self._round_id[instance] *= Proposer.primes[self.id - 1]
        # Discard all promises and accept messages received for previous round
        self._promises_received[instance] = 0
        self._accept_messages_current_round[instance] = 0

        prepare_message = Prepare(sender=self,
                                  receiver_role=Role.ACCEPTOR,
                                  payload=PreparePayload((self._round_id[instance], instance))
                                  )
        self.send(prepare_message)
        # Register time of prepare
        self._last_prepare_time[instance] = time.time()
        self.log("Started round {0} for instance {1}, with requested value {2}"
                 .format(self._round_id[instance], instance, self._client_requests[instance])
                 )

    def propose_phase_parallel(self, promise_message: Promise) -> None:
        payload: PromisePayload = promise_message.payload
        acceptor_round: RoundID = payload[0]
        round_accepted: RoundID = payload[1]
        value_accepted: PaxosValue = payload[2]
        instance: InstanceID = payload[3]

        if acceptor_round == self._round_id[instance]:
            self._promises_received[instance] += 1

            if round_accepted > self._latest_promise[instance][0]:
                self._latest_promise[instance][0] = round_accepted
                self._latest_promise[instance][1] = value_accepted

        if self._promises_received[instance] == self.net.quorum_size:
            # Set value to propose next to the value received accepted in the highest round, if any, otherwise use
            # value requested by the clint
            if self._latest_promise[instance][0] == RoundID(0):
                self._value_to_propose[instance] = self._client_requests[instance]
            else:
                self._value_to_propose[instance] = self._latest_promise[instance][1]

            propose_message = Propose(sender=self,
                                      receiver_role=Role.ACCEPTOR,
                                      payload=ProposePayload((self._round_id[instance],
                                                              self._value_to_propose[instance],
                                                              instance)
                                                             )
                                      )
            self.send(message=propose_message)
            self.log("Proposing value {0} for instance {1}".format(self._value_to_propose[instance], instance))

    def accept_phase_parallel(self, accept_message: Accept) -> None:
        payload: AcceptPayload = accept_message.payload
        acceptor_round: RoundID = payload[0]
        accepted_value: PaxosValue = payload[1]
        instance: InstanceID = payload[2]

        if acceptor_round == self._round_id[instance]:
            self._accept_messages_current_round[instance] += 1

            # if a quorum of acceptor accepted this value set this instance as decided
            if self._accept_messages_current_round[instance] == self.net.quorum_size:
                decide_message: Decide = Decide(sender=self,
                                                receiver_role=Role.LEARNER,
                                                payload=DecidePayload((accepted_value, instance))
                                                )
                self.send(decide_message)
                self.log("Sending DECIDE({0}) to learners for instance {1}".format(accepted_value, instance))

                self._undecided_instances.remove(instance)
                self._decided_values[instance] = accepted_value

    def check_for_timeouts(self) -> None:
        """
        Check for the first undecided instance that timed out and start a new round for it
        :return:
        """
        for instance in self._undecided_instances:
            if (time.time() - self._last_prepare_time[instance]) > self._round_timeouts[instance]:
                print('\033[93m' + "Instance {0} round {1} exceeded timeout!".format(instance, self._round_id[instance]) + "\033[0m")
                self._round_timeouts[instance] *= Proposer.TIMEOUT_GROWTH_FACTOR
                self.prepare_phase_parallel(instance)
                break

    def run(self) -> NoReturn:
        self.log('Start running...')

        while True:
            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)

            self.check_for_timeouts()
