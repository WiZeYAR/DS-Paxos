#!/bin/bash

# ---- VARIABLES ---- #
NETWORK_SIZE=2
SELF_ROLE="proposer"
SELF_ID=$1
CONFIG_PATH=$2
PLR=$3
LIFETIME=$4
DISABLE_TIMEOUT=$5
DISABLE_PREEXECUTION=$6

# ---- PROGRAM EXECUTION ---- #
python3 ./main.py $SELF_ROLE $SELF_ID $CONFIG_PATH $NETWORK_SIZE $PLR $LIFETIME $DISABLE_TIMEOUT $DISABLE_PREEXECUTION
