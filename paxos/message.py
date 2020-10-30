from abc import ABC as Abstract, abstractmethod
from copy import deepcopy
from typing import NewType
from typing import Tuple

from paxos.message_type import MessageType
from paxos.role import Role
from paxos.node import Node, NodeID

# Round ID type.
# This is a measure of message "Freshness".
RoundID = NewType('RoundID', int)

# PaxosValue type
# Candidate value to be decided by Paxos
PaxosValue = NewType('PaxosValue', int)


# PInstance ID.
# This explains, to which paxos agreement instance this message belong.
InstanceID = NewType('InstanceID', int)


# Message payload.
# This is a package, sent in a datagram.
# Consists of sequence id, aka timestamp,
# paxos id, and the proposed or decided paxos value.
PreparePayload = NewType('PreparePayload', Tuple[RoundID, InstanceID])
PromisePayload = NewType('PromisePayload', Tuple[RoundID, RoundID, PaxosValue, InstanceID])
ProposePayload = NewType('ProposePayload', Tuple[RoundID, PaxosValue, InstanceID])
AcceptPayload = NewType('AcceptPayload', Tuple[RoundID, PaxosValue, InstanceID])
ClientProposePayload = NewType('ClientProposePayload', Tuple[PaxosValue, InstanceID])
DecidePayload = NewType('DecidePayload', Tuple[PaxosValue, InstanceID])


class Message(Abstract):
    """
    Immutable message type, which is composed and received by Nodes.
    """

    # ---- Constructors ---- #

    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 message_type: MessageType
                 ) -> None:
        """
        Default constructor
        """
        self.__sender_id = sender.id
        self.__sender_role = sender.role
        self.__receiver_role = receiver_role
        self.__message_type = message_type

    # ---- Public readonly fields ---- #

    @property
    def sender_id(self) -> NodeID:
        """
        Gets the id of the
        """
        return deepcopy(self.__sender_id)

    @property
    def sender_role(self) -> Role:
        """
        Gets the role of receiver
        """
        return deepcopy(self.__sender_role)

    @property
    def receiver_role(self) -> Role:
        return deepcopy(self.__receiver_role)

    @property
    def message_type(self) -> MessageType:
        return deepcopy(self.__message_type)

    @property
    @abstractmethod
    def payload(self):
        raise NotImplementedError


class Prepare(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: PreparePayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.PREPARE)
        self.__payload = payload

    @property
    def payload(self) -> PreparePayload:
        return self.__payload


class Promise(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: PromisePayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.PROMISE)
        self.__payload = payload

    @property
    def payload(self) -> PromisePayload:
        return self.__payload


class Propose(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: ProposePayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.PROPOSE)
        self.__payload = payload

    @property
    def payload(self) -> ProposePayload:
        return self.__payload


class Accept(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: AcceptPayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.ACCEPT)
        self.__payload = payload

    @property
    def payload(self) -> AcceptPayload:
        return self.__payload


class ClientPropose(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: ClientProposePayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.CLIENT_PROPOSE)
        self.__payload = payload

    @property
    def payload(self) -> ClientProposePayload:
        return self.__payload


class Decide(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: DecidePayload
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.DECIDE)
        self.__payload = payload

    @property
    def payload(self) -> DecidePayload:
        return self.__payload


class RequestAck(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: InstanceID
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.REQUEST_ACK)
        self.__payload = payload

    @property
    def payload(self) -> InstanceID:
        return self.__payload

class DecideAck(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: InstanceID
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.DECIDE_ACK)
        self.__payload = payload

    @property
    def payload(self) -> InstanceID:
        return self.__payload

class HeartBeat(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: int
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.HEARTBEAT)
        self.__payload = payload

    @property
    def payload(self) -> int:
        return self.__payload
