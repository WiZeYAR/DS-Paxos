#!/bin/bash

export CONFIG_PATH=./paxos/paxos.conf

N_VALUES=100
LIFETIME_DEFAULT=50
PLR_DEFAULT=0.0
NO_TIMEOUTS=1
NO_PRE_EXECUTION=0
FIRST_INSTANCE_DEFAULT=1

if [[ x$LIFETIME == "x" ]]; then
  LIFETIME="$LIFETIME_DEFAULT"
fi

if [[ x$PLR == "x" ]]; then
  PLR="$PLR_DEFAULT"
fi

if [[ x$FIRST_INSTANCE == "x" ]]; then
  FIRST_INSTANCE_DEFAULT="$FIRST_INSTANCE_DEFAULT"
fi

resultdir=./results
mkdir $resultdir
  rm -r $resultdir/*

if [ "$ROLE" = "client" ]; then

  if [ "$ID" = 2 ]; then
    sleep 20
    FIRST_INSTANCE=$(($N_VALUES + 1))
    LIFETIME=30
  fi

  ./generate.sh $N_VALUES > "$resultdir"/propose"$ID".txt

  # Wait for other processes to come alive
  sleep 5
  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME $FIRST_INSTANCE < "$resultdir"/propose"$ID".txt

elif [ "$ROLE" = "proposer" ]; then

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME $NO_TIMEOUTS $NO_PRE_EXECUTION

elif [ "$ROLE" = "learner" ]; then

  if [ "$ID" = 2 ]; then
    sleep 20
    LIFETIME=30
  fi

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME

else

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME
fi
