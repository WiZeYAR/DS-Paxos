#!/usr/bin/env python3

import sys
import pickle
from typing import List, Dict
from os import  path

from utils import ColoredString

def load_proposed_values(n_clients: int) -> List[List[int]]:
    proposed_values: List[List[int]] = [[] for i in range(n_clients)]

    for i in range(1,n_clients+1):
        if not path.exists('results/propose{0}.txt'.format(i)):
            print("File {0} not found! Exiting".format('results/propose{0}.txt'.format(i)))
            return None

        with open('results/propose{0}.txt'.format(i), "r") as file:
            for line in file:
                proposed_values[i-1].append(int(line.strip()))

    return proposed_values


def load_decided_values(n_learners: int, max_instance: int) -> List[Dict[int,int]]:
    decided_values: List[Dict[int, int]] = []

    for i in range(1, n_learnes+1):
        if not path.exists('results/learner{0}_decided_value'.format(i)):
            print("File {0} not found! Exiting".format('results/learner{0}_decided_value'.format(i)))
            return None

        with open('results/learner{0}_decided_value'.format(i), "rb") as file:
            decided_values.append(pickle.load(file=file))

        for instance in range(1, max_instance+1):
            if instance not in decided_values[i-1]:
                decided_values[i-1][instance] = None

    return decided_values

def print_decided_values(decided_values: List[Dict[int, int]], max_instance: int, n_learners: int) -> None:

    for instance in range(1, max_instance+1):

        str = "Instance: {0:5} |".format(instance)
        for learner in range(n_learnes):
            if decided_values[learner][instance] is not None:
                str += "  {0:7}  ".format(decided_values[learner][instance])
            else:
                str += ColoredString.color_string("  {0}  ".format(decided_values[learner][instance]), ColoredString.WARNING)
        print(str)


def print_consensus_property(integrity, agreement, termination, termination_ratio):
    print("Integrity: " +
          ColoredString.color_string("{0}".format(integrity),
                                     ColoredString.GREEN if integrity else ColoredString.FAIL)
          )
    print("Agreement: " +
          ColoredString.color_string("{0}".format(agreement),
                                     ColoredString.GREEN if agreement else ColoredString.FAIL)
          )
    print("Termination: " +
          ColoredString.color_string("{0} ({1}%)".format(termination, termination_ratio),
                                     ColoredString.GREEN if termination else ColoredString.FAIL)
          )


if __name__ == '__main__':
    assert len(sys.argv) >= 3,\
        'Usage: n_learners n_clients [print decided value] [list of starting instance number for each client]'

    n_learnes: int = int(sys.argv[1])
    n_clients: int = int(sys.argv[2])
    n_values: List[int] = []
    first_instance: List[int] = []
    print_values: bool = bool(sys.argv[3]) if len(sys.argv) >= 4 else False

    pos = 4
    while len(sys.argv) >= (pos+1):
        first_instance.append(int(sys.argv[pos]))
        pos += 1

    if len(first_instance) == 0:
        for client in range(n_clients):
            first_instance.append(1)
    assert len(first_instance) == n_clients, "Either specify first instance for all clients or for none"



    learners_out_files: List[str] = []
    clients_in_files: List[str] = []

    proposed_values: List[List[int]] = load_proposed_values(n_clients)
    if proposed_values is None:
        exit()

    max_instance = 0
    for c in range(n_clients):
        n_values.append(len(proposed_values[0]))
        if first_instance[c] - 1 + n_values[c] > max_instance:
            max_instance = first_instance[c] + n_values[c] -1
    print(max_instance)



    decided_values: List[Dict[int, int]] = load_decided_values(n_learnes, max_instance)
    if decided_values is None:
        exit()

    integrity = True
    agreement = True
    termination = True
    n_decided = 0

    for i in range(max_instance):
        instance = i + 1

        values = []
        for learner in range(n_learnes):
            # Append value decided by this learner to the list of decided values for this instance
            if decided_values[learner][instance] not in values:
                values.append(decided_values[learner][instance])

            # If a learner did not decide for an instance, TERMINATION is not satisfied
            if decided_values[learner][instance] is None:
                termination = False
            else:
                # If a value was decided check if integrity is preserved
                integrity = False
                for client in range(n_clients):
                    if first_instance[client] < i < first_instance[client] + n_values[client] - 1:
                        if proposed_values[client][i-first_instance[client]+1] == int(decided_values[learner][instance]):
                            integrity = True

        # If more than one value has been decided for this instance, agreement is violated
        if len(values) == 1 and None not in values:
            n_decided += 1
        else:
            values.remove(None)

        if len(values) > 1:
            agreement = False


    termination_ratio = n_decided / max_instance * 100.0

    print_consensus_property(integrity, agreement, termination, termination_ratio)


    if print_values:
        print_decided_values(decided_values, max_instance, n_learnes)
        print_consensus_property(integrity, agreement, termination, termination_ratio)


