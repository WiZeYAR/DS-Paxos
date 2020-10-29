#!/usr/bin/env python3

import sys
import pickle
from typing import List, Dict

def load_proposed_values(n_clients: int) -> List[List[int]]:
    proposed_values: List[List[int]] = [[] for i in range(n_clients)]

    for i in range(1,n_clients+1):
        file = open('results/propose{0}.txt'.format(i), "r")

        for line in file:
            proposed_values[i-1].append(int(line.strip()))

    return proposed_values


def load_decided_values(n_learners: int, n_values: int) -> List[Dict[int,int]]:
    decided_values: List[Dict[int, int]] = []

    for i in range(1, n_learnes+1):
        file = open('learner{0}_decided_value'.format(i), "rb")
        decided_values.append(pickle.load(file=file))
        file.close()

        for instance in range(1, n_values+1):
            if instance not in decided_values[i-1]:
                decided_values[i-1][instance] = None

    return decided_values

def print_decided_values(decided_values: List[Dict[int, int]], n_values: int, n_learners: int) -> None:
    for instance in range(1,n_values+1):
        for learner in range(n_learnes):
            pass

if __name__ == '__main__':
    assert len(sys.argv) >= 3,\
        'Usage: n_learners n_clients [learners output files] [client_input_files]'

    n_learnes: int = int(sys.argv[1])
    n_clients: int = int(sys.argv[2])

    learners_out_files: List[str] = []
    clients_in_files: List[str] = []

    proposed_values: List[List[int]] = load_proposed_values(n_clients)
    n_values = len(proposed_values[0])
    decided_values: List[Dict[int, int]] = load_decided_values(n_learnes, n_values)

    integrity = True
    agreement = True
    termination = True

    for i in range(n_values):
        instance = i + 1
        value = decided_values[0][instance]
        for learner in range(n_learnes):

            # If a lerner decided a different value AGREEMENT is not satisfied
            if decided_values[learner][instance] != value:
                agreement = False
            # If a learner did not decide for an instance, TERMINATION is not satisfied
            if decided_values[learner][instance] == None:
                termination = False
            else:
                # If a value was decided chack if integrity is preserved
                integrity = False
                for client in range(n_clients):
                    if proposed_values[client][i] == int(decided_values[learner][instance]):
                        integrity = True

        if not integrity and not agreement and not termination:
            break



    print("Integrity: {0}".format(integrity))
    print("Agreement: {0}".format(agreement))
    print("Termination: {0}".format(termination))

