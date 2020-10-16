from enum import Enum, unique


@unique
class Role(Enum):
    """
    A type, which defines the role of some node, or the node group.
    """
    CLIENT = 0  # Client node
    PROPOSER = 1  # Proposer node
    ACCEPTOR = 2  # Acceptor node
    LEARNER = 3  # Learner node
