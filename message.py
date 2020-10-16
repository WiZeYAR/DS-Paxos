from role import Role
from node import Node, NodeID
from copy import deepcopy
from typing import NewType, Tuple

# Sequence ID type.
# This is a measure of message "Freshness".
SeqID = NewType('SeqID', int)

# Paxos ID.
# This explains, to which paxos agreement process this message belong.
PaxosID = NewType('PaxosID', int)

# Message payload.
# This is a package, sent in a datagram.
# Consists of sequence id, aka timestamp,
# paxos id, and the proposed or decided paxos value.
Payload = NewType('Payload', Tuple[SeqID, PaxosID, str])


class Message:
    """
    Immutable message type, which is composed and received by Nodes.
    """

    # ---- Constructors ---- #

    def __init__(self,
                 sender: Node,
                 receiver_role: Role,
                 payload: Payload) -> None:
        """
        Default constructor
        """
        self.__sender_id = sender.id
        self.__sender_role = sender.role
        self.__receiver_role = receiver_role
        self.__payload = payload

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
    def payload(self) -> Payload:
        return deepcopy(self.__payload)
