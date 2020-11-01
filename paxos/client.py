from typing import NoReturn
from .role import Role
from .network import Network
from .node import NodeID, Node, MessageT
from .message import PaxosValue, InstanceID, ClientPropose, ClientProposePayload, MessageType

import time
import sys
from typing import Dict


class Client(Node):
    BASE_TIMEOUT = 0.5
    TIMEOUT_GROWTH_FACTOR = 2.0

    def __init__(self, id: NodeID, network: Network, plr: float, lifetime: float, first_instance: int = 1) -> None:
        super().__init__(id, Role.CLIENT, network, plr, lifetime)
        self._instance_id: InstanceID = InstanceID(first_instance-1)
        self._pending_requests: Dict[InstanceID, ClientPropose] = {}

        # Timeout for receiving an ACK for each instance value request
        self._request_timeouts: Dict[InstanceID, float] = {}
        self._last_request_time: Dict[InstanceID, float] = {}

    def request_value(self, value: int):
        """Send a request to all proposers to propose a given value"""
        self._instance_id += 1
        request_message: ClientPropose = ClientPropose(sender=self,
                                                       receiver_role=Role.PROPOSER,
                                                       payload=ClientProposePayload(
                                                           (PaxosValue(value), self._instance_id)
                                                       )
                                                       )
        self.send(request_message)
        self._pending_requests[self._instance_id] = request_message
        self._last_request_time[self._instance_id] = time.time()


    def run(self) -> NoReturn:
        self.log_info("Start running...")
        start = time.time()

        for value in sys.stdin:
            self.request_value(value.strip())
            self._request_timeouts[self._instance_id] = Client.BASE_TIMEOUT

        while True:
            if self.lifetime > 0.0:
                if time.time()-start > self.lifetime:
                    self.log_warning("Terminating...")
                    break

            # If an ACK is received remove request for the corresponding instance from the set of pending request
            message: MessageT = self.listen()
            if message is not None and message.message_type is MessageType.REQUEST_ACK:
                instance: InstanceID = message.payload
                if instance in self._pending_requests:
                    del self._pending_requests[instance]

            # Check if a value request timed out
            for instance in self._pending_requests.keys():
                if (time.time() - self._last_request_time[instance]) > self._request_timeouts[instance]:
                    # Increase timeout and try resend the request
                    self._request_timeouts[instance] *= Client.TIMEOUT_GROWTH_FACTOR
                    self.send(self._pending_requests[instance])





