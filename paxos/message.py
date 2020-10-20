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

# Paxos ID.
# This explains, to which paxos agreement process this message belong.
PaxosID = NewType('PaxosID', int)

# Message payload.
# This is a package, sent in a datagram.
# Consists of sequence id, aka timestamp,
# paxos id, and the proposed or decided paxos value.
PreparePayload = NewType('PreparePayload', Tuple[RoundID])
PromisePayload = NewType('PromisePayload', Tuple[RoundID, RoundID, PaxosValue])
ProposePayload = NewType('ProposePayload', Tuple[RoundID, PaxosValue])
AcceptPayload = NewType('AcceptPayload', Tuple[RoundID, PaxosValue])


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
                 payload: PaxosValue
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.CLIENT_PROPOSE)
        self.__payload = payload

    @property
    def payload(self) -> PaxosValue:
        return self.__payload


class Deliver(Message):
    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: PaxosValue
                 ) -> None:
        super().__init__(sender, receiver_role, message_type=MessageType.DELIVER)
        self.__payload = payload

    @property
    def payload(self) -> PaxosValue:
        return self.__payload
