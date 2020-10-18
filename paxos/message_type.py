from enum import Enum, unique

@unique
class MessageType(Enum):
    """
    The type defining the kind of messages sent by Paxos nodes
    """
    CLIENT_PROPOSE = 4
    PREPARE = 0
    PROMISE = 1
    PROPOSE = 2
    ACCEPT = 3
