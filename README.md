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

Clients can take an additional argument specifying the instance number to start with when assigning instances to the values to request to the proposers (by default they start from 1); this can be used to make some client request value for the first n instances and later make another client request values for the following n instances.  Additionally a client is expected to be launched by redirecting into stdin the content of a txt file with all the values that it is supposed to request. For example the following command launches a client proposing from instance 101:

```./client.sh 1 paxos/paxos.conf 0.0 60 101 < results/propose1.txt &```

Proposers can be launched with 2 additional arguments (fifth and sixth argument), the first to disable the timeouts (suggested if no package is lost) and the second to disable pre-execution of phase 1 for debugging (value 1 and 0 will disable and leave enabled the feature respectively). For example, the following launches a proposer with no timeouts and using pre-execution:

```./proposer.sh 1 paxos/paxos.conf 0.0 20 1 0```

### Launching Multi-Paxos locally and verifying the execution

Script ```run.sh``` allows to start a simple paxos execution with 2 clients, 4 proposers, 3 acceptors and 2 learners that takes the following arguments to customize the execution:
1. The project directory, `.` expected
2. The number of values to propose per client
3. (optional) The lifetime of all the nodes 
4. (optional) Flag to disable timeouts, (1 means disable timeouts)
5. (optional) Flag to disable pre-execution of phase 1, (1 means disable)

For example the following command starts an execution with 1000 instances (each clients tries to request 1000 values), running for 30 seconds with loss ratio of 10% and timouts and pre-execution enabled:

```./run.sh . 1000 30 0.1 0 0```

The Python script ```check_results.py``` can be used to test whether the previously run Paxos execution satisfied integrity, agreement and termination (as a percentage of the requested values that were decided), it takes the following arguments:
1. the number of learners
2. number of clients
3. (optional) whether to print the decided value
4. (optional) a list with the starting instance number for each client, required if a client started from a custom initial instance

For example, the following command check the results for an execution with two learners, two clients one of which requested 100 instances values starting from instance 1 and the other requested other 100 instance values but starting from instance 101:
```./check_results.py 2 2 true 1 101```

The folder ```test_runs``` contains a set of of scripts for running and verifying a set of example executions (suggested tests in the handout), which do not take any argument.

### Launching Multi-Paxos in docker containers
A docker-compose file is provided in which all the processes for which a container should be created are defined. The image of each service is created through the ```Dockerfile```: when a container is started an entrypoint script is executed, which executes the bash script to launch the correct role and, more in general, defines what each process (in its own container) should do in a similar fashion to what the ```run.sh``` script does when running paxos locally. Two entrypoint script are already defined in the ```Docker_entrypoints``` folder. The execution of the processes can be changhed by modifying the entry point script, in particular, all the input arguments that the script launching each role takes (i.e. lifetime, num of values, etc.), are defined there once for all the processes: this is done becouse typically all processes are run with equal arguments and so this allows to easily change the execution behaviour by modifying a single variable. See the provided entrypoint script for reference. To use a different entry poitn script modify the last line of the ```Dockerfile```.

To build the docker compose images run 
```docker-compose build```
then to start the containers run
```docker-compose up -d```

Once the containers terminate the executions, the script ```copy_results_from_containers.sh``` can be used to copy the input/output files storing the execution record from each container to the host ```results``` directory by providing the number of clients and learners in that order:

```./copy_results_from_containers.sh 2 2```

Finally the execution can be verifyied running 

```./check_results.py 2 2 true ```

If the ```docker-entrypoint_catchup.sh``` is used, run ```./check_results.py 2 2 true 1 101 ```.


## Implementation Details
Here we first describe the organization of this project repository, then we describe our implementation of multi-paxos by describing all the features implemented on top of what would be a standard Paxos algorithm (not described here).

### Structure of the project
The ```paxos.conf``` file defines the multicast address group for each role. The ```main.py``` is the entry point for running each process, it takes care of parsing all the input arguments and executing the correct modules to provide the functionality specified by the input arguments. All the python modules implementing the multi-paxos logic are collected insde the ```paxos``` folder: 
- the ```network.py``` module defines the Network class which contains the multicast group (IP + port) for each role and provide two static methods to create the sender and receiver UDP sockets for exchanging packets using IP multicast
- the ```message.py``` and ```message_type.py``` modules defines the classes for all the different message type exchanged by the processors (i.e. promise, decide, heartbeats, etc.) as sub-class of an abstarct message parent class carrying a specific payload; in particular each message object embeds the multicast group of the receiver that is used to send the message to the correct group of processes
- the ```role.py``` file defines the enum for the 4 differnt node roles in Paxos
- the ```node.py``` modules defines the abstract node class, which implement the listen and send methods that hide the low level message transmition routines, involving message serialization and socket calls, and defines an abstarct run method
- the ```client.py```, ```proposer.py```, ```acceptor.py``` and ```learner.py``` modules, finally, all inherit from the parent ```Node``` class and implement the run method for each Paxos role; when starting a process through the bash script, the ```main.py``` script invokes the run method from one of these modules according the the role given as input


 
 ### Starting multiple instances at the same time
 Paxos allows to make all learners decide on the same values among the set of proposed values, this can be extend to make the learnes decide an array of values instead, such that they all decide the same values and in the same order, by executing a full Paxos instance for each position in the array. In principle, all the Paxos instances are independent from one another and could be executed in parallel, however, care must be taken to guarantee that the learners decide values in the same order. To avoid running the Paxos instances in a sequential fashion to satisfy this condition, we made the clients assign an incremental instance number to each value that they are going to request to the proposers and modified the basic paxos algorithm to use separate variables for each instance (all message bar hearbeats carry the corresponding instance number as well). In this way, multiple instances can be started at the same time and the learners will know to which instance a decided value corresponds to, regerdless of the order in which it decided it. Of course learners may not learn in time the decided values for some instances and only a subset of the lerners may learn the decided value for a given instance (not against agreement) due to lost messages, however, this is not a problem, since they can always recover the total order by knowing if there was a previous instances for which they did not learn the decided value. 
 
Therefore, in our implementation, the clients are the one responsible for defining instances and, in particular, we assumed that only the i-th value given in input to the clients can be decided for the i-th instance for simplicity: this is not a limitation since multi-paxos does not make any specification on which one of all the possible total orderings should be chosen. WE assume that all clients request the same number of values, however, this is not required by our algorithm. By defaul, clientsassign instance number starting from 1, this can be modified by passing an extra argument to ```client.sh``` specifying the initial instance number (this is used for example in the `test_runs\test_6\run_catchup.sh` to simulate a scenario totest learner catchup).
 
 
 

 ### Checking the correctness of a Paxos execution
 
For each client that has to be started, the script ```generate.sh``` is used to randomly select some number of values which are written, one per line, in a text file, then the content of the corresponing file is directed to the stdin of the client process upon launch; **this is the expected way to provide values to request to the clients**. Each learner, instead, writes its dictionary of instance-value pairs to a file `learnerID_decided_value` whenever a new value is decided. These files are saved insde a ```results``` directory and are used by the ```check_results.py``` scripts to verify if the corresponding Paxos execution satisfies integrity, agreement and temrination. First, the script reads the propose text file to discover all the instance numbers requested by clients (using the initial instance number of each client for more complex scenarios, see `test_runs\test_6\run_catchup.sh`), then creates a matrix where for each instance the value decided, if any, by each learner is stored, then finally it checks that:
 1. for each decided value, there is a client which requested it for the corresponding instance (**integrity**)
 2. the set of decided values for each instance contains at most one value other than `None` (**agreement**)
 3. the percentage of instances for which all learners decided the same value (**termination**)
 

 
 ### Electing a leader
 
 In order to guarantee termination of each Paxos instance, we implemented a leader election oracle for the proposers based on heartbeats and timeouts. Each proposer periodically sends an heartbeat to all other proposers containing its ID while at the same time it listens for the incoming hearbeats and keeps track of the set of prodosers IDs from which it received an heartbeat recently; if a proposer does not receive an heartbeat from the leader for a long time, then it selects the new leader as the proposer with smaller ID among those it is aware of (exluding the id of the leader that timed out). On initialization our implementation assumes that the propsoer with ID 1 is the leader for simplicity, however, even if proposer 1 is not alive it does not undermine termination (launching a proposer with id 1 is suggested anyway to take advantage of phase 1 pre execution). 
This is a best effort approach, since it is not possible to guarntee that no two proposers ever believe both to be the leader (especially with a lossy netwrok), but in practice it shuold happen rarely.
 
 ### Dealing with lossy networks
 
In order to deal with lossy networks where some messages may get lost, the leader proposer uses a timeout mechanism to start a new round for some instance whenever it does not receive in time an ACK message from a learner for the current round, confirming that it learnt the decided the value for that instance. The same ACK/timeout mechanism is also used to make clients keep re-trying sending requests to proposers until the proposers collectively received all requests; in particular, by making only the leader proposer send the ACK to the clients for each value request received, it is possible to guarantee that after enough time, the leader proposer will have received a reqeust for a value to propose for each instance. This mechanisms guarantee that eventually all leanrners will **collectively** decide all the values, however, this time, it cannot guarantee that each single learners decides all values: the reason behind this is that the leader proposer is not guaranteed to know exactly how many learners are alive at any given moment, so it cannot expect to receive an ack for each instance from each learner and so it can only wait the ack from one of the learners per instance. 

Of course, introducing timeouts for handling message losses reduces the performance of the algorithm and the choice of the timeout value is critical: timeout should grow exponentically to make sure that eventually a round that requires a lot of time (i.e. due to high load or slow network) manages to be completed, while on the other hand using fixed small timeouts allows to make a lot of trials to counteract the message loss randomness. A flag is provided to disable timeouts for better performance when no message loss is expected.
 
 ### Learner catch-up
 
 In order to implement a mechanism that allows learners that lag behind to catch up, we used the same heartbeat/timeouts technique used for the proposer to be able to also elect a leader among the learners, then we modified the learners so that only the leader is allowed to send an ACK to the proposers when it learns a new decided value: overall this has the effect of making the leader learner eventually learn all the decided values in most cases (selecting a new leader may cause problems). Then, periodically, each learner sends a catch-up request to the leader (learner), which responds back with the list of (numbered) decided values that the learner can use to update its local knowledge. Again, this is a best effort implementation, since the leader may fails and more than one learner may think to be the leader, but in practice it works well. It is important to note that catch-up is a very expensive operation and so it is (should be) done relatively rarely, since the leader have to send over the network a message with all its decided values which may get very heavy (indeed we split this message in fixed sized small chuncks). Alternative approaches can be used, for example by making the leader send only the missing decided values, but this would require learners to send their list of known decided instances in the request, so it would not make much difference performance-wise.
 
 ### Pre-executing phase 1
In order to improve the performance of the algorithm, we implemented the execution in advance of phase 1: the leader proposer, when receives the first request by a client, sends a prepare message for the corresponding instance to the acceptors and then waits for receivng their promises, on success, the round id is saved and the leader can start all subsequent instances directly from phase 2 using the stored round ID. This optimization has a huge impact on performance, especially when the number of values is large, however, it must be disabled when a new leader is elected because the previous leader may still be alive and running phase 2 with a lower round ID. Launching a proposer with id 1 is suggested (otherwise a new leader is elected and pre-execution disabled). Pre-execution of phase 1 is also disabled for simplicity on round timeout (when many timeouts occur pre-exuction becomes complex and provide diminished gains in performance). 
