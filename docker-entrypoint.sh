#!/bin/bash

export CONFIG_PATH=./paxos/paxos.conf
bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME
