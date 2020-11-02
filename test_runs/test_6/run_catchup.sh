#!/usr/bin/env bash


conf=./paxos/paxos.conf
n=100
plr=0.0
resultdir=./results
time=30
no_timeouts=0
no_prexecution=0



# following line kills processes that have the config file in its cmdline
KILLCMD="pkill -f $conf"

$KILLCMD

mkdir $resultdir
rm -r $resultdir/*


./generate.sh $n > "$resultdir"/propose1.txt
./generate.sh $n > "$resultdir"/propose2.txt

echo "Starting acceptors..."

./acceptor.sh 1 $conf $plr $time &
./acceptor.sh 2 $conf $plr $time &
./acceptor.sh 3 $conf $plr $time &

echo "Starting acceptors...DONE"
sleep 1

echo "Starting first learner..."

./learner.sh 1 $conf  $plr $time &

echo "Starting first learner...DONE"

sleep 1
echo "Starting proposers..."

./proposer.sh 1 $conf $plr $time $no_timeouts $no_prexecution &

echo "Starting proposers...DONE"


echo "Waiting to start first client"
sleep 3

echo "Starting first client..."

./client.sh 1 $conf $plr $time < "$resultdir"/propose1.txt &

echo "Starting first client...DONE"

sleep 10

echo "Starting second learner..."

./learner.sh 2 $conf  $plr $time &

echo "Starting second learner...DONE"
sleep 1

echo "Waiting to start second client"
sleep 3
echo "Starting second client..."

./client.sh 2 $conf $plr $time $((n+1)) < "$resultdir"/propose2.txt &

echo "Starting second client...DONE"

sleep 10


$KILLCMD
wait

./check_results.py 2 2 true $n $((n+1))