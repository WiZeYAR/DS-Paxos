from typing import NoReturn, NewType, TypeVar
from copy import deepcopy
from abc import ABC as Abstract, abstractmethod
from paxos.network import Network
from paxos.role import Role
from utils import ColoredString

import pickle
import logging
import socket
import random


NodeID = NewType('NodeID', int)

MessageT = TypeVar('MessageT', bound='Message')

class Node(Abstract, ):
    # ---- Constructor ---- #

    def __init__(self,
                 id: NodeID,
                 role: Role,
                 network: Network,
                 plr: float = 0.0,
                 lifetime: float =0.0) -> None:
        """
        Default constructor
        """
        self.__id = id
        self.__role = role
        self.__net = network

        assert 0.0 <= plr < 1.0, "Package loss ratio should be between 0 and 1 (excluded)"
        self._package_loss_ratio = plr

        assert lifetime >= 0.0, "Positive lifetime expected!"
        self.__lifetime = lifetime

        group_sock_address = self.__net[self.__role]
        self.__receiver_socket = Network.multicast_receiver_socket(group_sock_address)
        self.__sender_socket = Network.udp_sender_socket()

        # --- Create logger --- #
        self.__logger = logging.getLogger("{0} {1}".format(self.__role.value, self.__id), )
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.WARNING)

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

    @property
    def lifetime(self) -> float:
        return self.__lifetime

    def log_debug(self, message: str):
        self.__logger.debug(message)

    def log_warning(self, message: str):
        self.__logger.warning(ColoredString.color_string(message, ColoredString.WARNING))

    def log_info(self, message: str):
        self.__logger.info(message)

    # ---- Public methods ---- #
    def listen(self) -> MessageT:
        """
        Starts listening on the network.
        When message is received -- returns it.
        This process blocks the paxos.
        """
        message = None
        # Try to receive a message
        try:
            message_raw = self.__receiver_socket.recv(Network.SOCKET_BUFFSIZE)
        except socket.error:
            pass
        # If no errors, aka, message received parse it
        else:
            # Randomly drop the incoming message according to the package loss ratio to emulate an unreliable network
            # for debug purposes
            if random.random() >= self._package_loss_ratio:
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



