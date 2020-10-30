#!/usr/bin/env python3

from typing import NoReturn, Dict
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import MessageType, RoundID, PaxosValue, InstanceID
from .message import Accept, AcceptPayload, Decide, DecidePayload, RequestAck
import pickle

class Learner(Node):
    def __init__(self, id: NodeID, network: Network, plr: float) -> None:
        super().__init__(id, Role.LEARNER, network, plr)
        self._message_callbacks = {
            MessageType.ACCEPT: self.accept_phase_parallel,
            MessageType.DECIDE: self.decide
        }
        self._decided_values: Dict[InstanceID, PaxosValue] = {}
        self._accept_messages_received: Dict[InstanceID, Dict[RoundID, int]] = {}

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
            self.log("DECIDED value {0} for instance {1}".format(self._decided_values[instance], instance))

            file = open('learner{}_decided_value'.format(self.id), "wb")
            pickle.dump(dict(sorted(self._decided_values.items())), file=file)
            file.close()

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
            file = open('learner{}_decided_value'.format(self.id), "wb")
            pickle.dump(dict(sorted(self._decided_values.items())), file=file)
            file.close()

            # send ACK to proposers for current instance
            ack_message: RequestAck = RequestAck(sender=self,
                                                 receiver_role=Role.PROPOSER,
                                                 payload=instance)
            self.send(ack_message)


    def run(self) -> NoReturn:
        self.log("Start running...")
        while True:
            message: MessageT = self.listen()
            if message is not None and message.message_type in self._message_callbacks:
                self._message_callbacks[message.message_type](message)


