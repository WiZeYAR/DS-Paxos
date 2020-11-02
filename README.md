# Multi-Paxos

This repository contains an implemntation of Multi-Paxos designed to be fairly robust to the most common failure cases. It allows to start a process that runs executing one of the four Paxos roles (client, proposer, acceptor and learner), simulate different Multi-Paxos executions by starting some number of processes/ nodes with different configurations and verify the correctness of the results.

## Launching Multi-Paxos

### Starting the individual nodes
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

### Launching Multi-Paxos locally and verifying the execution

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

### Launching Multi-Paxos in docker containers
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


## Implementation Details

The ```paxos.conf``` file defines the multicast address group for each role. The ```main.py``` is the entry point for running each process, it takes care of parsing all the input arguments and executing the correct modules to provide the functionality specified by the input arguments. All the python modules implementing the multi-paxos logic are collected insde the ```paxos``` folder: 
- the ```network.py``` module defines the Network class which contains the multicast group (IP + port) for each role and provide two static methods to create the sender and receiver UDP sockets for exchanging packets using IP multicast
- the ```message.py``` and ```messate_type.py``` modules defines the classes for all the different message type exchanged by the processors (i.e. promise, decide, heartbeats, etc.) as sub-class of an abstarct message parent class carrying a specific payload; in particular each message object embeds the multicast group of the receiver that is used to send the message to the correct group of processes
- the ```role.py``` file defines the enum for the 4 differnt node roles in Paxos
- the ```node.py``` modules defines the abstract node class, which implement the listen and send methods hiding the low level message transmition routines performing message serialization and socket calls and defines an abstarct run method
- the ```client.py```, ```proposer.py```, ```acceptor.py``` and ```learner.py``` modules, finally, all inherit from the parent ```Node``` class and implement the run method for each Paxos role; when starting a process through the bash script, the ```main.py``` script invokes the run method from one of these modules according the the role given as input

 
 ### Starting multiple instances at the same time
 

 ### Checking the correctness of a Paxos execution
 
 For each client that has to be started, the script ```generate.sh``` is used to randomly select some number of values which are written, one per line in a text file, then the content of the corresponing file is directed to the stdin of the client process upon launch. Each earner, instead, writes its dictionary of instance-value pairs to a file 'learnerID_decided_value' whenever a new value is decided. These files are saved insde a ```results``` directory and are used by the ```check_results.py``` scripts to verify if the corresponding Paxos execution satisfies integrity, agreement and temrination. First, the script reads the propose text file to discover all the instance numbers requested by clients (using the initial instance number of each client for more complex scenarios), then creates a matrix where for each instance and the value decided, if any, by each learner is stored, then finally it checks that:
 1. for each decided value, there is a client which requested it for the corresponding instance (integrity)
 2. the set of decided values for each instance containsat most one value othern than `None` (agreement)
 3. the percentage of instances for which all learners decided the same value (termination)
 

 
 ### Electing a leader
 
 ### Dealing with lossy networks
 
 ### Learner catch-up
 
 ### Pre-executing phase 1

