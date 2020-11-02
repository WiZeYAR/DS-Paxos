#!/bin/bash

export CONFIG_PATH=./paxos/paxos.conf

n=1000
PLR=0.0
LIFETIME=60
resultdir=./results
no_timeouts=1
no_pre_execution=0
first_instance=1


mkdir $resultdir
  rm -r $resultdir/*

if [ "$ROLE" = "client" ]; then

  ./generate.sh $n > "$resultdir"/propose"$ID".txt
  # Wait for other processes to come alive
  sleep 5
  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME $first_instance < "$resultdir"/propose"$ID".txt

elif [ "$ROLE" = "proposer" ]; then

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME $no_timeouts $no_pre_execution

elif [ "$ROLE" = "learner" ]; then

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME

else

  bash "./$ROLE.sh" $ID $CONFIG_PATH $PLR $LIFETIME
fi
