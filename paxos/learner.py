#!/usr/bin/env python3

from typing import NoReturn, Dict, List
from copy import deepcopy
import time

from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import MessageType, RoundID, PaxosValue, InstanceID
from .message import Accept, AcceptPayload, Decide, DecidePayload, RequestAck, HeartBeat, CatchupRequest, \
    CatchupResponse
import pickle


class Learner(Node):
    HEARTBEAT_RATE = 0.33
    HEARTBEAT_TIMEOUT = 4.0
    CATCHUP_RATE = 3.0
    CATCHUP_TIMEOUT = 0.5
    CATCHUP_RESPONSE_MAX_ITEMS = 250  # ~ 2kB message

    def __init__(self, id: NodeID, network: Network, plr: float, lifetime: float) -> None:
        super().__init__(id, Role.LEARNER, network, plr, lifetime)
        self._message_callbacks = {
            MessageType.ACCEPT: self.accept_phase_parallel,
            MessageType.DECIDE: self.decide,
            MessageType.HEARTBEAT: self.heartbeat_handler,
            MessageType.CATCHUP_REQUEST: self.catchup_request_callback,
            MessageType.CATCHUP_RESPONSE: self.catchup_response_callback
        }
        self._decided_values: Dict[InstanceID, PaxosValue] = {}
        self._accept_messages_received: Dict[InstanceID, Dict[RoundID, int]] = {}

        # Perform leader election by continuously sending an heartbeat to other learners, if an heartbeat from the
        # leader is not received for enough time a new leader is elected
        self._leader_id: int = 0
        self._known_learners: List[int] = [self.id]
        self._last_heartbeat_sent: float = 0.0
        self._last_heartbeat_leader: float = time.time()

        self._time_last_catchup_sent: float = 0.0

    def accept_phase_parallel(self, accept_message: Accept) -> None:
        payload: AcceptPayload = accept_message.payload
        acceptor_round: RoundID = payload[0]
        accepted_value: PaxosValue = payload[1]
        instance: InstanceID = payload[2]

        if instance not in self._accept_messages_received:
            self._accept_messages_received[instance] = {}
            self._accept_messages_received[instance][acceptor_round] = 1
        elif acceptor_round not in self._accept_messages_received[instance]:
            self._accept_messages_received[instance][acceptor_round] = 1
        else:
            self._accept_messages_received[instance][acceptor_round] += 1

        if self._accept_messages_received[instance][acceptor_round] == self.net.quorum_size:
            self._decided_values[instance] = accepted_value
            self.log_debug("DECIDED value {0} for instance {1}".format(self._decided_values[instance], instance))

            file = open('results/learner{}_decided_value'.format(self.id), "wb")
            pickle.dump(dict(sorted(self._decided_values.items())), file=file)
            file.close()

            if self.id == self._leader_id:
                # send ACK to proposers for current instance
                ack_message: RequestAck = RequestAck(sender=self,
                                                     receiver_role=Role.PROPOSER,
                                                     payload=instance)
                self.send(ack_message)

    def decide(self, decide_message: Decide) -> None:
        payload: DecidePayload = decide_message.payload
        decided_value: PaxosValue = payload[0]
        instance: InstanceID = payload[1]

        if instance not in self._decided_values.keys():
            self._decided_values[instance] = decided_value
            file = open('results/learner{}_decided_value'.format(self.id), "wb")
            pickle.dump(dict(sorted(self._decided_values.items())), file=file)
            file.close()

            if self.id == self._leader_id:
                # send ACK to proposers for current instance
                ack_message: RequestAck = RequestAck(sender=self,
                                                     receiver_role=Role.PROPOSER,
                                                     payload=instance)
                self.send(ack_message)

    # --- LEADER ELECTION ORACLE LOGIC --- #
    def send_heartbeat(self) -> None:
        if (time.time() - self._last_heartbeat_sent) > Learner.HEARTBEAT_RATE or self._last_heartbeat_sent == 0.0:
            heatbeat: HeartBeat = HeartBeat(sender=self,
                                            receiver_role=Role.LEARNER,
                                            payload=self.id)
            self.send(heatbeat)
            self._last_heartbeat_sent = time.time()

    def heartbeat_handler(self, hearbeat: HeartBeat) -> None:
        id: float = hearbeat.payload

        if id not in self._known_learners:
            self._known_learners.append(id)

        if id == self._leader_id:
            self._last_heartbeat_leader = time.time()

    def check_leader_timeout(self) -> None:
        if self.id == self._leader_id:
            return

        if (time.time() - self._last_heartbeat_leader) > self.HEARTBEAT_TIMEOUT:
            if self._leader_id in self._known_learners:
                self._known_learners.remove(self._leader_id)
            self._leader_id = min(self._known_learners)
            self.log_warning("Elected learner {0} as the new leader".format(self._leader_id, self.id))
            self.send_heartbeat()
            self._last_heartbeat_sent = time.time()
            self._last_heartbeat_leader = time.time()

    # ------------------------------------ #

    # --- LEARNER CATCH-UP LOGIC --- #
    def send_catchup_request(self) -> None:
        if self.id == self._leader_id:
            return

        if (time.time() - self._time_last_catchup_sent) > Learner.CATCHUP_RATE:
            catchup_request: CatchupRequest = CatchupRequest(sender=self,
                                                             receiver_role=Role.LEARNER,
                                                             payload=None
                                                             )
            self.send(catchup_request)
            self._time_last_catchup_sent = time.time()

    def catchup_request_callback(self, request: CatchupRequest) -> None:
        if self.id is not self._leader_id:
            return

        # Response may get too big, so it is split into multiple messages
        max_len = Learner.CATCHUP_RESPONSE_MAX_ITEMS
        n_chunks = len(self._decided_values) // max_len

        for i in range(n_chunks):
            if (time.time() - self._time_last_catchup_sent) > Learner.CATCHUP_RATE:
                chunk: Dict[InstanceID, PaxosValue] = {k:self._decided_values[k] for k in list(
                    self._decided_values.keys())[max_len * i:max_len * i + max_len]
                                                       }
                catchup_response: CatchupResponse = CatchupResponse(sender=self,
                                                                    receiver_role=Role.LEARNER,
                                                                    payload=deepcopy(chunk))

                self.send(catchup_response)
        if len(self._decided_values) % max_len > 0:
            chunk: Dict[InstanceID, PaxosValue] = {k: self._decided_values[k] for k in list(
                self._decided_values.keys())[max_len * n_chunks:]
                                                   }
            catchup_response: CatchupResponse = CatchupResponse(sender=self,
                                                                receiver_role=Role.LEARNER,
                                                                payload=deepcopy(chunk))

            self.send(catchup_response)

    def catchup_response_callback(self, response: CatchupResponse) -> None:
        sender_id: int = response.sender_id
        decided_values: Dict[InstanceID, PaxosValue] = response.payload
        if sender_id is not self._leader_id:
            return

        self._decided_values.update(decided_values)

        file = open('results/learner{}_decided_value'.format(self.id), "wb")
        pickle.dump(dict(sorted(self._decided_values.items())), file=file)
        file.close()

    def check_catchup_timeout(self):
        if not self._last_catchup_acked and (time.time() - self._time_last_catchup_sent) > Learner.CATCHUP_TIMEOUT:
            # send new catch up
            Learner.CATCHUP_TIMEOUT *= 2.0
            self.send_catchup_request()

    # ---------------------------------- #

    def run(self) -> NoReturn:
        self.log_info("Start running...")
        start = time.time()

        self._last_heartbeat_leader: float = time.time()
        while True:
            if self.lifetime > 0.0:
                if time.time()-start > self.lifetime:
                    self.log_warning("Terminating...")
                    break

            self.send_heartbeat()
            self.send_catchup_request()

            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)

            self.check_leader_timeout()
