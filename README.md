# Fault Tolerant Key-value Store

# Description:
 
## Partiton-tolerance, Availability and Consistency
This key-value store is fault tolerant: it will continue functioning in the face of network partitions and node failure.

## Problem introduction:
Due to the CAP theorem, we cannot have a fault tolerant key-value store that is both available and strongly consistent. In this implementation, we favor availability over strong consistency. This key-value store will always return responses to requests, even if the most recent data is not returned.
Even though we cannot guarantee strong consistency, it is possible to guarantee eventual consistency and convergence. Right after a network is healed, the key-value store can return stale data. However, the key-value store should guarantee that the data is up-to date after a time bound. In other words, the key-value store should have the property of bounded staleness. The time bound for this implementation is 10 seconds.

## Conflict Resolution
It is possible that after a network is healed, two nodes end up with different values for the same key. Such a conflict should be resolved using causal order, if it can be established. This is implemented via an internal vector clock and time stamps as a fallback. If the events are causally concurrent, then the tie will be resolved using the timestamps on replica nodes. 

Starting the key-value store
To start a key value store we use the following environmental variables.
* "K" is the number of replicas. There are two cases here:
* |Nodes| >= K:  In this case, K nodes in the system will behave as replicas and any remaining nodes behave as proxies.
* |Nodes| < K: In this case, the system will be operating in degraded mode and since we favor availability, we continue to accept writes in this mode.
 
 ## Api Initialization Schema
 
* "VIEW" is the list of ip:ports pairs of nodes.
* "IPPORT" is the ip address and port of the node.
An example of starting a key-value store with 4 nodes and K=3:
docker run -p 8081:8080 --ip=10.0.0.21 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.21:8080" mycontainer
docker run -p 8082:8080 --ip=10.0.0.22 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.22:8080" mycontainer
docker run -p 8083:8080 --ip=10.0.0.23 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.23:8080" mycontainer
docker run -p 8084:8080 --ip=10.0.0.24 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.24:8080" mycontainer
In the above example, you will assign three of nodes as replicas and one as proxy.

# API
## Key-value system correctness, operations and Unit Testing criteria
GET, PUT requests return extra information about the node that processed the write and causal order. The information used to establish causal order is stored in "causal_payload" and "timestamp" fields. The "causal_payload" field is used to establish causality between events. For example, if a node performs a write A followed by write B, then the corresponding causal payloads X_a and X_b should satisfy inequality X_a < X_b. Similarly, a causal payload X of a send event should be smaller that the causal payload Y of the corresponding receive event, i.e. X < Y. The value of the "causal_payload" field is solely depends on the mechanism you use to establish the causal order. The value of the "timestamp" field is the wall clock time on the replica that first processed the write.
To illustrate, let a client A writes a key, and a client B reads that key and then writes it, B's write should replace A's write (even if it lands on a different server). To make sure that this works, we will always pass the causal payload of previous reads into future writes. You must ensure that B's read returns a causal payload higher than the payload associated with A's write!
To consider another example, let 2 clients write concurrently to 2 different nodes respectively. And let T_1 and T_2 be the corresponding write timestamps measured according to the nodes' wall clocks. If T_1 > T_2 then the first write wins. If T_1 < T_2 then the second write wins. However, how can we resolve the writing conflict if T_1 == T_2? Can we use the identity of the nodes?
For better performance, no matter which node is queried, sharding and redirection of requests may increase performance so all replicas handle approximately equal number of requests.
 
* A GET request to "/kv-store/<key>" with the data field "causal_payload=<causal_payload>" retrieves the value that corresponds to the key. The "causal_payload" data field is the causal payload observed by the client’s most recent read or write operation. A response object has the following fields: "result", "value", "node_id", "causal_payload", "timestamp". A response to a successful request looks like this: 
```
    {
    "result":"success",
    "value":1,
    "node_id": 3,
    "causal_payload": "1.0.0.4",
    "timestamp": "1256953732"
    }
```
* A PUT request to "/kv-store/<key>" with the data fields "val=<value>" and "causal_payload=<causal_payload>" creates a record in the key value store. The "causal_payload" data field is the causal payload observed by the client’s most recent read or write operation (why we need it? See the example above). If the client did not do any reads, then the causal payload is an empty string. The response object has the following fields: "result", "node_id", "causal_payload", "timestamp". An example of a successful response looks like:
```
    {
    "result":"success",
    "node_id": 3,
    "causal_payload": "1.0.0.4",
    "timestamp": "1256953732"
    }
```
* DELETE. You do not need to implement deletion of keys in this assignment.
 
## Obtaining replica information
The following methods are implemented to expose information about the nodes to the external world:
 
* A GET request on "/kv-store/get_node_details" returns if the node is a replica or forwarding instance. For example, a successful response for the following curl request curl -X GET http://localhost:8083/kv-store/get_node_details 
```
    {
    "result":"success",
    "replica": "No" // "No" for a forwarding instance, "Yes" for a replica
    }
```
* A GET request on "/kv-store/get_all_replicas" returns a list all replicas in the system. 
```
    {
    "result":"success",
    "replicas": ["10.0.0.21:8080", "10.0.0.22:8080", "10.0.0.23:8080"]
    }
```
## Adding and Deleting nodes
We use "update_view" request to add and delete nodes. For example, let’s say we started a key value-store with 3 nodes, so the value of K=3. If we add a new node, then number of nodes in the system increases, as a result the following happen:
       1. The new node converges on the keys in the key-value store if it is to be a replica. ( |Nodes| <= K )
       2. The new node behaves as proxy if it is to be a proxy ( |Nodes| > K )
* A PUT request on "/kv-store/update_view?type=add" with the data payload "ip_port=<ip_port>" adds the node to the key-value store. A successful response returns the node id of the new node, and the total number of nodes. It should look like:
```
    {
    "msg":"success",
    "node_id": 3,
    "number_of_nodes": 4,
    }
```
* A PUT request on "/kv-store/update_view?type=remove" with the payload "ip_port=<ip_port>" removes the node. It decrements the number of nodes and a  successful response object contains the total number of nodes after the deletion, for example:
```
    {
    "result":"success",
    "number_of_nodes": 2
    }
```
Error Responses
All error responses contain 2 fields "result" and "msg". The msg field contains the details about the error, for example:
```
    {
    "result":"error",
    "msg":"key value store is not available:
    }
```
