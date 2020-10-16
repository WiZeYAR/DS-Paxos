from typing import Tuple
from typing import NoReturn, NewType
from copy import deepcopy
from abc import ABC as Abstract, abstractmethod
from paxos.network import Network
from paxos.role import Role


NodeID = NewType('NodeID', int)


class Node(Abstract):

    # ---- Constructor ---- #

    def __init__(self,
                 id: NodeID,
                 role: Role,
                 network: Network) -> None:
        """
        Default constructor
        """
        self.__id = id
        self.__role = role
        self.__net = network

    # ---- Public properties ---- #

    @property
    def id(self) -> NodeID:
        deepcopy(self.__id)

    @property
    def role(self) -> Role:
        deepcopy(self.__role)

    @property
    def net(self) -> Network:
        self.__net

    # ---- Public methods ---- #

    def listen(self) -> 'Message':
        """
        Starts listening on the network.
        When message is received -- returns it.
        This process blocks the paxos.
        """
        raise NotImplementedError

    def send(self, group: Role, message: 'Message') -> None:
        """
        Sends message to the group.
        """
        raise NotImplementedError

    # ---- Public abstract methods ---- #

    @abstractmethod
    def run(self) -> NoReturn:
        """
        Starts this paxos.
        This method never returns.
        """
        pass


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
