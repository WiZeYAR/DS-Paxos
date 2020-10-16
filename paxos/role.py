from enum import Enum, unique


@unique
class Role(Enum):
    """
    A type, which defines the role of some paxos, or the paxos group.
    """
    CLIENT = 0  # Client paxos
    PROPOSER = 1  # Proposer paxos
    ACCEPTOR = 2  # Acceptor paxos
    LEARNER = 3  # Learner paxos
