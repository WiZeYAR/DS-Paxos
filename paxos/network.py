from typing import Tuple, NewType
from paxos.role import Role
from copy import deepcopy


NetworkGroup = NewType('NetworkGroup', Tuple[str, int])


class Network:
    def __init__(self,
                 clients: NetworkGroup,
                 proposers: NetworkGroup,
                 acceptors: NetworkGroup,
                 learners: NetworkGroup):
        """
        Default constructor
        """
        self.__dict = {
            Role.CLIENT: clients,
            Role.PROPOSER: proposers,
            Role.ACCEPTOR: acceptors,
            Role.LEARNER: learners,
        }

    def __getitem__(self, role: Role) -> NetworkGroup:
        """
        Gets a network group data by role
        """
        return deepcopy(self.__dict[role])
