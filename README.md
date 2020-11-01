# DS-Paxos

## Launching the nodes

To start a process in any of the 4 roles launch the corresponding bash script with 4 arguments
1. Process id
2. Path to config file
3. Package loss ratio, between 0.0 and 1.0 (excluded), which is used to simulate unreliable networks
4. Lifetime, time in seconds after which the process will terminate

For example to launch a learner with 10% loss ratio for 20 sec:

```./learner.sh 1 paxos/paxos.conf 0.10 20```

Additionally proposer can take 2 additional argument to disable timeouts (suggested if plr=0.0) and disable pre-execution respectively:

```./proposer.sh 1 paxos/paxos.conf 0.0 20 1 0```

and client can take an additional argument to specify from which instance to start when proposing (default 1).
