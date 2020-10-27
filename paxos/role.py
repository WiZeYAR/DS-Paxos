from enum import Enum, unique


@unique
class Role(Enum):
    """
    A type, which defines the role of some paxos, or the paxos group.
    """
    CLIENT = 'CLIENT'  # Client paxos
    PROPOSER = 'PROPOSER'  # Proposer paxos
    ACCEPTOR = 'ACCEPTOR'  # Acceptor paxos
    LEARNER = 'LEARNER'  # Learner paxos
