from typing import NoReturn, NewType, TypeVar
from copy import deepcopy
from abc import ABC as Abstract, abstractmethod
from paxos.network import Network
from paxos.role import Role

import pickle
import logging
import socket


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

        # --- Create logger --- #
        self.__logger = logging.getLogger("{0}_{1}".format(self.__role.value, self.__id), )
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(name)s - %(message)s'))
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.DEBUG)

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

    def log(self, message: str):
        self.__logger.debug(message)

    # ---- Public methods ---- #
    def listen(self) -> MessageT:
        """
        Starts listening on the network.
        When message is received -- returns it.
        This process blocks the paxos.
        """
        message = None
        try:
            message_raw = self.__receiver_socket.recv(Network.SOCKET_BUFFSIZE)
        except socket.error:
            pass
        else:
            message = pickle.loads(message_raw)
        return message


    def send(self, message: MessageT) -> None:
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



