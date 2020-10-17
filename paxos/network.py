from typing import Tuple, NewType
from paxos.role import Role
from copy import deepcopy
import socket
import struct

NetworkGroup = NewType('NetworkGroup', Tuple[str, int])


class Network:
    SOCKET_BUFFSIZE = 2**16

    def __init__(self,
                 size: int,
                 clients: NetworkGroup,
                 proposers: NetworkGroup,
                 acceptors: NetworkGroup,
                 learners: NetworkGroup):
        """
        Default constructor
        """
        self.__size = size
        self.__dict = {
            Role.CLIENT: clients,
            Role.PROPOSER: proposers,
            Role.ACCEPTOR: acceptors,
            Role.LEARNER: learners,
        }

    def __len__(self):
        return self.__size

    def __getitem__(self, role: Role) -> NetworkGroup:
        """
        Gets a network group data by role
        """
        return deepcopy(self.__dict[role])

    @staticmethod
    def udp_sender_socket() -> socket.SocketType:
        """
        Create UDP socket
        """
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    @staticmethod
    def multicast_receiver_socket(socket_address: NetworkGroup) -> socket.SocketType:
        """
        Create multicast receiver socket
        """
        mcast_receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mcast_receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mcast_receiver_sock.bind(socket_address)

        # create multicast group and add the receiver socket to it
        mcast_group_ip = socket_address[0]
        mcast_group = struct.pack("4sl", socket.inet_aton(mcast_group_ip), socket.INADDR_ANY)
        mcast_receiver_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mcast_group)

        return mcast_receiver_sock


