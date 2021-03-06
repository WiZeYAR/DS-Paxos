#!/usr/bin/env python3

# ---- IMPORTS ---- #
from paxos import Role, Network, NetworkGroup, Client, Proposer, Acceptor, Learner, Node
import sys
import os

# ---- OBTAINING PARAMETERS ---- #
#print('Obtaining parameters')

assert len(sys.argv) >= 5, \
    'There must be at least 5 program arguments (including the program name)'
(self_role,
 self_id,
 config_path,
 quorum_size) = (sys.argv[1],
                  int(sys.argv[2]),
                  sys.argv[3],
                  int(sys.argv[4]))

if len(sys.argv) >= 6:
    plr = float(sys.argv[5])
else:
    plr = 0.0

if len(sys.argv) >= 7:
    lifetime = float(sys.argv[6])
else:
    lifetime = 0.0

if self_role == "proposer":
    if len(sys.argv) >= 8:
        disable_timeouts = bool(int(sys.argv[7]))
    else:
        disable_timeouts = False

    if len(sys.argv) >= 9:
        disable_preexecution = bool(int(sys.argv[8]))
    else:
        disable_preexecution = False

if self_role == "client":
    if len(sys.argv) >= 8:
        first_instance = int(sys.argv[7])
    else:
        first_instance = 1

assert self_role in ['client', 'proposer', 'acceptor', 'learner'], \
    'Argument at index 1 must define the paxos\'s role'

assert self_id > 0, \
    'Argument at index 2 must be a number, defining paxos\'s id, and must not be negative'

assert os.path.isfile(config_path), \
    'Argument at index 3 must point to the file'

assert quorum_size > 0, \
    'Argument at index 4 must define the size of the quorum of acceptors in the network, and must be bigger than 0'

"""
print(f'''
Current paxos state: 
    Role:\t\t{self_role}
    Id:\t\t\t{self_id}
    Config:\t\t{config_path}
    Quorum size:\t{quorum_size}
''')

# ---- SETTING UP NETWORK ---- #
print('Performing network setup')
"""

network: Network = None
with open(config_path) as file:
    groups = {}
    for line in file:
        if line == '':
            continue
        group, addr, port, *_ = line.split()
        groups[group] = NetworkGroup((addr, int(port)))
    network = Network(quorum_size,
                      groups['clients'],
                      groups['proposers'],
                      groups['acceptors'],
                      groups['learners'])

assert network is not None, 'Failed to parse network config file'

"""
print(f'''
Current network state:
    Quorum size:\t\t{quorum_size}
    Clients:
        Addr: {network[Role.CLIENT][0]}
        Port: {network[Role.CLIENT][1]}
    Proposers:
        Addr: {network[Role.PROPOSER][0]}
        Port: {network[Role.PROPOSER][1]}
    Acceptors:
        Addr: {network[Role.ACCEPTOR][0]}
        Port: {network[Role.ACCEPTOR][1]}
    Learners:
        Addr: {network[Role.LEARNER][0]}
        Port: {network[Role.LEARNER][1]}
''')
"""

# ---- SETTING UP INSTANCE ---- #
paxos_node: Node = (Client(self_id, network, plr, lifetime, first_instance) if self_role == 'client'
                    else Proposer(self_id, network, plr, lifetime, disable_timeouts, disable_preexecution) if self_role == 'proposer'
                    else Acceptor(self_id, network, plr, lifetime) if self_role == 'acceptor'
                    else Learner(self_id, network, plr, lifetime)
                    )

# ---- RUNNING THE INSTANCE ---- #
paxos_node.run()
