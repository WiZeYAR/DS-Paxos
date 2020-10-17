from typing import NoReturn, NewType, TypeVar
from copy import deepcopy
from abc import ABC as Abstract, abstractmethod
from paxos.network import Network
from paxos.role import Role

import pickle


NodeID = NewType('NodeID', int)

MessageT = TypeVar('MessageT', bound='Message')

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

        group_sock_address = self.__net[self.__role]
        self.__receiver_socket = Network.multicast_receiver_socket(group_sock_address)
        self.__sender_socket = Network.udp_sender_socket()

    # ---- Public properties ---- #

    @property
    def id(self) -> NodeID:
        return deepcopy(self.__id)

    @property
    def role(self) -> Role:
        return deepcopy(self.__role)

    @property
    def net(self) -> Network:
        return self.__net


    # ---- Public methods ---- #
    def listen(self) -> MessageT:
        """
        Starts listening on the network.
        When message is received -- returns it.
        This process blocks the paxos.
        """
        message_raw = self.__receiver_socket.recv(Network.SOCKET_BUFFSIZE)
        message = pickle.loads(message_raw)
        return message


    def send(self, group: Role, message: MessageT) -> None:
        """
        Sends message to the group.
        """
        receiver_address = self.__net[message.receiver_role]
        message_raw = pickle.dumps(obj=message)
        self.__sender_socket.sendto(message_raw, receiver_address)

    # ---- Public abstract methods ---- #

    @abstractmethod
    def run(self) -> NoReturn:
        """
        Starts this paxos.
        This method never returns.
        """
        pass



