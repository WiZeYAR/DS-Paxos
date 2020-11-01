#!/usr/bin/env bash

#!/usr/bin/env bash

conf=./paxos/paxos.conf
n=100
plr=0.0
resultdir=./results
time=10
no_timeouts=1
no_prexecution=0


# following line kills processes that have the config file in its cmdline
KILLCMD="pkill -f $conf"

$KILLCMD

echo "Running with 1000 values and only 2 accpetors"

mkdir $resultdir
rm -r $resultdir/*


./generate.sh $n > "$resultdir"/propose1.txt
./generate.sh $n > "$resultdir"/propose2.txt

echo "starting acceptors..."

./acceptor.sh 1 $conf $plr $time &
./acceptor.sh 2 $conf $plr $time &

sleep 1
echo "starting learners..."

./learner.sh 1 $conf  $plr $time &
./learner.sh 2 $conf  $plr $time &



sleep 1
echo "starting proposers..."

./proposer.sh 1 $conf $plr $time $no_timeouts $no_prexecution &
./proposer.sh 2 $conf $plr $time $no_timeouts $no_prexecution &
./proposer.sh 3 $conf $plr $time $no_timeouts $no_prexecution &
./proposer.sh 4 $conf $plr $time $no_timeouts $no_prexecution &


echo "waiting to start clients"
sleep 3
echo "starting clients..."

./client.sh 1 $conf $plr $time < "$resultdir"/propose1.txt &
./client.sh 2 $conf $plr $time < "$resultdir"/propose2.txt &

sleep $time
sleep 5


$KILLCMD
wait



./check_results.py 2 2 true