from enum import Enum, unique

@unique
class MessageType(Enum):
    """
    The type defining the kind of messages sent by Paxos nodes
    """
    PREPARE = 0  # Client paxos
    PROMISE = 1  # Proposer paxos
    PROPOSE = 2  # Acceptor paxos
    ACCEPT = 3  # Learner