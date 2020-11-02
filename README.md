# DS-Paxos

## Launching the individual nodes
Four bash scripts are provided in order to start a single process executing one of the 4 Paxos role, all scripts can take in input 4 arguments:
1. The ID of the process within its group (i.e. proposers, learner, etc.)
2. The path to the config file specifying the IP multicast gorups
3. The package loss ratio (OPTIONAL), which can be used to simulate a lossy network and can be a value between 0.0 and 1.0 (excluded), where 0.0 means no message is loss; set to 0.0 by default if not specified
4. The lifetime of the node/process (OPTIONAL), defining the time in seconds after which the process will terminate; if not specified the process will keep running until manually killed

For example to launch a learner with 10% loss ratio which runs for 20 sec:

```./learner.sh 1 paxos/paxos.conf 0.10 20 &```

NOTE: The process IDs are assumed to start from 1 and be consecutive for clients and learners to easily access the corresponding input/output files when checking the resutls.

Clients can take an additional argument specifying the instance number to start with when assigning instances to the values to request to proposer, by default they start from 1; this can be used to make some client request value for the first n instances and later make another client request values for the following n instances.  Additionally a client is expected to be launched by redirecting into stdin the content of a txt file with all the values that it is supposed to request:

```./client.sh 1 paxos/paxos.conf 0.0 60 101 < results/propose1.txt &```

Also proposers can be launched with 2 additional arguments, the first to disable the timeouts (suggested if no package is lost) and the second to disable pre-execution of phase 1 for debugging, for example in orde rto launch a proposer with no timeouts and keeping pre-execution enabled:

```./proposer.sh 1 paxos/paxos.conf 0.0 20 1 0```

## Launching and testing a full Paxos execution

Script ```run.sh``` allows to start a simple paxos execution with 2 clients, 4 proposers, 3 acceptors and 2 learners that takes the following arguments to customize the paxos execution:
1. The project directory, `.` expected
2. The number of values to propose per client
3. (optional) The lifetime of all the nodes 
4. (optional) Flag to disable timeouts, (1 means disable timeouts)
5. (optional) Flag to disable pre-execution of phase 1, (1 means disable)

```./run.sh . 1000 30 0.1 0 0```

The Python script ```check_results.py``` can be used to test whether the previous Paxos execution satisfied integrity, agreement and termination (as a percentage of the requested values that were decided), it takes the following arguments
1. the number of learners
2. number of clients
3. (optional) whether to print the decided value
4. (optional) a list with the starting instance number for each client, required if a client started from a custom initial instance

```./check_results.py 2 2 true ```

The folder ```test_runs``` contains a set of of scripts for running and verifying a set of example executions, which do not take any argument.

## Running the nodes in docker containers
A docker-compose file is provided in which all the processes for which a container should be created are defined. The image of each service is created through the ```Dockerfile```: when a container is started an entrypoint script is executed, which executes the bash script to launch the correct role and mor ein general defines what each process (in its own container) should do in a similar fashion to what the ```run.sh``` script does when running paxos locally. Two entrypoint script are already defined in the ```Docker_entrypoints``` folder. The execution of the processes can be changhed by modifying the entry point script, in particular all the input arguments that the script launching each role takes (i.e. lifetime, num of values, etc.) are defined there once for all the processes, since typically all processes are run with equal arguments, this allows to easily change the execution behaviour by modifying a single variable.
To use a different entry poitn script modify the ```Dockerfile```.

To build the docker compose images run 
```docker-compose build```
then to start the containers run
```docker-compose up -d```

Once the containers terminate the executions, the script ```copy_results_from_containers.sh``` can be used to copy the input/output files storing the execution record from each container to the host ```results``` directory by providing the number of clients and learners:

```./copy_results_from_containers.sh 2 2```

Finally the execution can be verifyied running 

```./check_results.py 2 2 true ```

If the ```docker-entrypoint_catchup.sh``` is used, run ```./check_results.py 2 2 true 1 101 ```.
