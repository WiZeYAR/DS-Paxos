from typing import NoReturn, NewType
from copy import deepcopy
from abc import ABC as Abstract, abstractmethod
from message import Message
from network import Network
from role import Role


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

    def listen(self) -> Message:
        """
        Starts listening on the network.
        When message is received -- returns it.
        This process blocks the node.
        """
        raise NotImplementedError

    def send(self, group: Role, message: Message) -> None:
        """
        Sends message to the group.
        """
        raise NotImplementedError

    # ---- Public abstract methods ---- #

    @abstractmethod
    def run(self) -> NoReturn:
        """
        Starts this node.
        This method never returns.
        """
        pass
