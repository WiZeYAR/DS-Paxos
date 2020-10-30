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
paxos_node: Node = (Client(self_id, network, plr) if self_role == 'client'
                    else Proposer(self_id, network, plr) if self_role == 'proposer'
                    else Acceptor(self_id, network, plr) if self_role == 'acceptor'
                    else Learner(self_id, network, plr)
                    )

# ---- RUNNING THE INSTANCE ---- #
paxos_node.run()
