#!/usr/bin/env bash

projdir="$1"
conf=./paxos/paxos.conf
n="$2"
plr="$3"
resultdir=./results

if [[ x$projdir == "x" || x$n == "x" || x$plr == "x" ]]; then
	echo "Usage: $0 <project dir> <number of values per proposer> <plr>"
    exit 1
fi

# following line kills processes that have the config file in its cmdline
KILLCMD="pkill -f $conf"

$KILLCMD


cd $projdir || exit
mkdir $resultdir
rm -r $resultdir/*


./generate.sh $n > "$resultdir"/propose1.txt
./generate.sh $n > "$resultdir"/propose2.txt

echo "starting acceptors..."

./acceptor.sh 1 $conf $plr &
./acceptor.sh 2 $conf $plr &
./acceptor.sh 3 $conf $plr &

sleep 1
echo "starting learners..."

./learner.sh 1 $conf  $plr &
./learner.sh 2 $conf  $plr &


sleep 1
echo "starting proposers..."

./proposer.sh 1 $conf $plr &
./proposer.sh 2 $conf $plr &
./proposer.sh 3 $conf $plr &
#./proposer.sh 4 $conf $plr &
#./proposer.sh 5 $conf $plr &
#./proposer.sh 6 $conf $plr &


echo "waiting to start clients"
sleep 3
echo "starting clients..."

./client.sh 1 $conf $plr < "$resultdir"/propose1.txt &
./client.sh 2 $conf $plr < "$resultdir"/propose2.txt &


sleep 30

$KILLCMD
wait

