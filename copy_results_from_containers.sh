#!/usr/bin/env bash

CLIENTS=$1
LEARNERS=$2

if [[ x$CLIENTS == "x" || x$LEARNERS == "x" ]]; then
	echo "Usage: $0 <number of clients> <number of learners> <plr>"
    exit 1
fi

#mkdir $resultdir
rm -r resultdir/*

for ((id=1;id<=$CLIENTS;id++)); do
  docker cp client"$id":/app/results/propose"$id".txt results/propose"$id".txt
  echo "copied data for client$id"
done

for ((id=1;id<=$LEARNERS;id++)); do
  docker cp learner"$id":/app/results/learner"$id"_decided_value results/learner"$id"_decided_value
  echo "copied data for learner $id"
done
