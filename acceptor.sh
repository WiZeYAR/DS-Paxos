#!/bin/bash

# ---- VARIABLES ---- #
NETWORK_SIZE=3
SELF_ROLE="acceptor"
SELF_ID=$1
CONFIG_PATH=$2

# ---- PROGRAM EXECUTION ---- #
python ./main.py $SELF_ROLE $SELF_ID $CONFIG_PATH $NETWORK_SIZE
