from typing import NoReturn, List, Dict
import time

from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message_type import MessageType
from .message import RoundID, PaxosValue, InstanceID, ClientPropose, ClientProposePayload
from .message import PreparePayload, Prepare, Propose, ProposePayload
from .message import Promise, PromisePayload, Accept, AcceptPayload, Decide, DecidePayload
from .message import RequestAck, DecideAck, HeartBeat

class Proposer(Node):
    # Naive solution to guarantee uniqueness of round ID between multiple proposers
    primes = [2, 3, 5, 7, 11, 13, 17, 19 , 23, 29, 31]
    BASE_TIMEOUT = 1.5
    TIMEOUT_GROWTH_FACTOR = 2.0
    HEARBEAT_RATE = 0.33
    HEARTBEAT_TIMEOUT = 4.0
    PREPARE_PHASE1_IN_ADVANCE = True

    def __init__(self, id: NodeID, network: Network, plr: float, lifetime: float,
                 disable_timeout: bool = False, disable_pre_execution: bool = False) -> None:
        super().__init__(id, Role.PROPOSER, network, plr, lifetime)
        self.disable_timout = disable_timeout

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

        # Timeout between sending the decide message to the learner and receiving the ACK; If everything works fine
        # the learner should learn the decided value directly from the acceptors, but if something goes wrong (i.e.
        # message is lost) it relies on the proposer to recover the decided value
        self._acked_decided_values: Dict[InstanceID, bool] = {}
        self._last_decide_time: Dict[InstanceID, float] = {}
        self._learners_decide_timeout: Dict[InstanceID, float] = {}

        self._leader_id: int = 1
        self._known_proposers: List[int] = [self.id]
        self._last_heartbeat_sent: float = 0.0
        self._last_heartbeat_leader: float = time.time()

        # Pre-prepare phase 1 flag
        self._phase1_preprepared: bool = False
        self._phase1_preprepared_round: RoundID = None
        self._enable_phase1_optimization = Proposer.PREPARE_PHASE1_IN_ADVANCE and not disable_pre_execution


        # Dictionary containing the callbacks to be executed for each type of message received
        self._message_callbacks = {
            MessageType.CLIENT_PROPOSE: self.client_request_callback,
            MessageType.PROMISE: self.propose_phase_parallel,
            MessageType.ACCEPT: self.accept_phase_parallel,
            MessageType.DECIDE_ACK: self.decide_ack_handler,
            MessageType.HEARTBEAT: self.heartbeat_handler
        }

    def client_request_callback(self, client_request: ClientPropose):
        payload: ClientProposePayload = client_request.payload
        value: PaxosValue = payload[0]
        instance: InstanceID = payload[1]


        if self.id == self._leader_id:
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
            self._acked_decided_values[instance] = False

            self._round_id[instance] = RoundID(1)
            self._value_to_propose[instance] = None
            self._promises_received[instance] = 0
            self._latest_promise[instance] = [RoundID(0), None]
            self._last_prepare_time[instance] = 0.0
            self._round_timeouts[instance] = 1.0*Proposer.BASE_TIMEOUT if not self.disable_timout else float('inf')
            self._learners_decide_timeout[instance] = 1.0*Proposer.BASE_TIMEOUT
            self._accept_messages_current_round[instance] = 0


            if self.id == self._leader_id:
                if not self._enable_phase1_optimization:
                    self.prepare_phase_parallel(instance)
                    return

                if self._phase1_preprepared is not True:
                    self.pre_prepare_phase1(instance)

                if self._phase1_preprepared:
                    promise: Promise = Promise(sender=self,
                                               receiver_role=Role.PROPOSER,
                                               payload=PromisePayload((self._phase1_preprepared_round,
                                                                       RoundID(0),
                                                                       None,
                                                                       instance))
                                               )
                    self._round_id[instance] = self._phase1_preprepared_round
                    self._last_prepare_time[instance] = time.time()
                    self.propose_phase_parallel(promise_message=promise)


    # --- PHASE 1A, 2a and 3 ---- #
    def pre_prepare_phase1(self, instance: InstanceID):
        """
        Run a prepare phase for this instance and wait to get a promises from a quorum, while still sending and
        receiving heartbeats :param instance: :return:
        """
        self.prepare_phase_parallel(instance, preprepare=True)

        promises = 0
        start = time.time()
        while promises < self.net.quorum_size and (time.time() - start) < self._round_timeouts[instance]:
            if self.lifetime > 0.0:
                if (time.time()-self.start_time) > self.lifetime:
                    return

            self.send_heartbeat()

            message: MessageT = self.listen()
            if message is not None and message.message_type is MessageType.PROMISE:
                promises += 1

            self.check_heartbeat()

        if promises < self.net.quorum_size:
            self._enable_phase1_optimization = False
            self.log_warning("Unable to receive in time enough promises to execute phase 1 in advance, "
                             "optimization disabled!")
            self._phase1_preprepared = False
            return

        self._last_prepare_time[instance] = time.time()
        self._phase1_preprepared_round = self._round_id[instance]
        self._phase1_preprepared = True

    def prepare_phase_parallel(self, instance: InstanceID, preprepare: bool= False) -> None:
        # Start new round
        self._round_id[instance] *= Proposer.primes[self.id - 1]
        # Discard all promises and accept messages received for previous round
        self._promises_received[instance] = 0
        self._accept_messages_current_round[instance] = 0

        prepare_message = Prepare(sender=self,
                                  receiver_role=Role.ACCEPTOR,
                                  payload=PreparePayload((self._round_id[instance], instance, preprepare))
                                  )
        self.send(prepare_message)
        # Register time of prepare
        self._last_prepare_time[instance] = time.time()
        self.log_debug("Started round {0} for instance {1}, with requested value {2}"
                 .format(self._round_id[instance], instance, self._client_requests[instance])
                 )

    def propose_phase_parallel(self, promise_message: Promise) -> None:
        payload: PromisePayload = promise_message.payload
        acceptor_round: RoundID = payload[0]
        round_accepted: RoundID = payload[1]
        value_accepted: PaxosValue = payload[2]
        instance: InstanceID = payload[3]

        # This proposer did not receive the request from the client for this instance
        if instance not in self._client_requests.keys():
            return

        if acceptor_round == self._round_id[instance]:
            self._promises_received[instance] += 1

            if round_accepted > self._latest_promise[instance][0]:
                self._latest_promise[instance][0] = round_accepted
                self._latest_promise[instance][1] = value_accepted

        if self._promises_received[instance] == self.net.quorum_size or self._phase1_preprepared:
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
                                                              instance,
                                                              self._phase1_preprepared and self._enable_phase1_optimization)
                                                             )
                                      )
            self.send(message=propose_message)
            self.log_debug("Proposing value {0} for instance {1}".format(self._value_to_propose[instance], instance))

    def accept_phase_parallel(self, accept_message: Accept) -> None:
        payload: AcceptPayload = accept_message.payload
        acceptor_round: RoundID = payload[0]
        accepted_value: PaxosValue = payload[1]
        instance: InstanceID = payload[2]

        # This proposer did not receive the request from the client for this instance
        if instance not in self._client_requests.keys():
            return

        if acceptor_round == self._round_id[instance]:
            self._accept_messages_current_round[instance] += 1

            # if a quorum of acceptor accepted this value set this instance as decided
            if self._accept_messages_current_round[instance] == self.net.quorum_size:
                self._undecided_instances.remove(instance)
                self._decided_values[instance] = accepted_value
                self._last_decide_time[instance] = time.time()

    # ---------------------------#

    # ---- Round timeout and Learner decide timeout ----- #

    def decide_ack_handler(self, ack: DecideAck) -> None:
        instance: InstanceID = DecideAck.payload
        self._acked_decided_values[instance] = True

    def check_for_timeouts(self) -> None:
        """
        Check for the first undecided instance that timed out and start a new round for it, then look among the
        decided instances not ACKed by a learner yet for all those which timed out while waiting for the ACK
        """

        if self.id != self._leader_id:
            return

        for instance in self._undecided_instances:
            if (time.time() - self._last_prepare_time[instance]) > self._round_timeouts[instance]:
                #print('\033[93m' + "Instance {0} round {1} exceeded timeout!".format(instance, self._round_id[instance]) + "\033[0m")
                self._round_timeouts[instance] *= Proposer.TIMEOUT_GROWTH_FACTOR
                self._enable_phase1_optimization = False
                self.prepare_phase_parallel(instance)
                # Handle a single time out per loop to improve responsiveness to input messages
                break

        for instance in self._decided_values.keys():
            if not self._acked_decided_values[instance]:
                if (time.time() - self._last_decide_time[instance]) > self._learners_decide_timeout[instance]:
                    # Timed out waiting the learner ACK: send the decided value to the learners and increase the timeout
                    self._learners_decide_timeout[instance] *= Proposer.TIMEOUT_GROWTH_FACTOR
                    decide_message: Decide = Decide(sender=self,
                                                    receiver_role=Role.LEARNER,
                                                    payload=DecidePayload((self._decided_values[instance], instance))
                                                    )
                    self.send(decide_message)

                    # Handle a single time out per loop to improve responsiveness to input messages
                    break

    # --------------------------------------------------- #

    # ----- LEADER ELECTION ORACLE --------------- #

    def send_heartbeat(self) -> None:
        if (time.time() - self._last_heartbeat_sent) > self.HEARBEAT_RATE or self._last_heartbeat_sent == 0.0:
            heatbeat: HeartBeat = HeartBeat(sender=self,
                                            receiver_role=Role.PROPOSER,
                                            payload=self.id)
            self.send(heatbeat)
            self._last_heartbeat_sent = time.time()

    def heartbeat_handler(self, hearbeat: HeartBeat) -> None:
        id: float = hearbeat.payload

        if id not in self._known_proposers:
            self._known_proposers.append(id)

        if id == self._leader_id:
            self._last_heartbeat_leader = time.time()

    def check_heartbeat(self):
        if self.id == self._leader_id:
            return

        if (time.time() - self._last_heartbeat_leader) > self.HEARTBEAT_TIMEOUT:
            self._phase1_preprepared = False
            # It is not safe to pre prepare again phase 1 beacouse the previous leader may still be active and there
            # is no way to know for sure the id of the last round in which it proposed!
            self._enable_phase1_optimization = False

            if self._leader_id in self._known_proposers:
                self._known_proposers.remove(self._leader_id)
            self._leader_id = min(self._known_proposers)
            self.log_warning("Elected proposer {0} as the new leader".format(self._leader_id, self.id))
            self.send_heartbeat()
            self._last_heartbeat_sent = time.time()
            self._last_heartbeat_leader = time.time()

    # -------------------------------------------- #

    def run(self) -> NoReturn:
        self.log_info('Start running...')

        # Warn user about disabled features
        if self.disable_timout:
            self.log_warning('Disabled round timeouts')
        if not self._enable_phase1_optimization:
            self.log_warning('Disabled phase 1 pre-execution')


        self.start_time = time.time()
        self._last_heartbeat_leader: float = time.time()

        while True:
            # Check for termination
            if self.lifetime > 0.0:
                if (time.time()-self.start_time) > self.lifetime:
                    self.log_warning("Terminating...")
                    break

            self.send_heartbeat()

            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)

            self.check_heartbeat()
            self.check_for_timeouts()
