#!/bin/bash

# ---- VARIABLES ---- #
NETWORK_SIZE=2
SELF_ROLE="acceptor"
SELF_ID=$1
CONFIG_PATH=$2
PLR=$3
LIFETIME=$4

# ---- PROGRAM EXECUTION ---- #
python3 -u ./main.py $SELF_ROLE $SELF_ID $CONFIG_PATH $NETWORK_SIZE $PLR $LIFETIME
