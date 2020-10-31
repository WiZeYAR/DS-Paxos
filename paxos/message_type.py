from enum import Enum, unique

@unique
class MessageType(Enum):
    """
    The type defining the kind of messages sent by Paxos nodes
    """

    PREPARE = 0
    PROMISE = 1
    PROPOSE = 2
    ACCEPT = 3
    CLIENT_PROPOSE = 4
    DECIDE = 5
    REQUEST_ACK = 6
    DECIDE_ACK = 7
    HEARTBEAT = 8
    CATCHUP_REQUEST = 9
    CATCHUP_RESPONSE = 10
