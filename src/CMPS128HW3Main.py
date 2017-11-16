"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

import logging
import threading

from CMPS128HW3KVSNodeDetails import CMPS128HW3KVSNodeDetails
from CMPS128HW3KVSGetAllReplicas import CMPS128HW3KVSGetAllReplicas
from CMPS128HW3KVSUpdateView import CMPS128HW3KVSUpdateView
from CMPS128HW3Node import CMPS128HW3Node
import CMPS128HW3Settings
# To prevent any errors, quick fix to patch the thread
import gevent.monkey; gevent.monkey.patch_thread()

import sys
sys.path.append('src/')

import os

from flask import Flask
from flask_restful import Api

"""
    Assignment 3
    ---------------
    A REST API service that serves as a fault tolerant key-value store (KVS) that is eventually consistent and a bounded
    staleness of 10 seconds. The KVS uses a vector clock protocol.
    
    Initiate the application with the appropriate KVS resource, logic to see if this instance is the main instance or
    a forwarding instance.

    Global variables (as listed in the settings file)
    -----------------------------------------------------
    :var localIPPort: The localIPPort for this specific instance in the form of IP:PORT (an identifier to query for objects)
    :var VCDict: All IP:PORT values and their associated vector clock values mapped in a global dictionary
    :var nodesList: All the IP:PORT values for all instances that exist in the KVS, as a list

    Local variables
    --------------------
    :var localIP: The local IP for this specific instance, by itself
    :var localPort: The local port for this specific instance, by itself
    :var viewList: Temporary list of initial nodes to be stored in the global nodesList
    :var numOfNodes: The number of total nodes/instances (or IP:PORT items) that exist in the KVS
    :var numOfReplicas: The number of desired instances to be replicas, as specified by the client   
"""
class CMPS128HW3Main:

    def __init__(self):

        # Initialize the application with the appropriate route
        app = Flask(__name__)
        api = Api(app)

        # Environment variables
        CMPS128HW3Settings.localIPPort = os.getenv('IPPORT')
        logging.debug("Value of IP:PORT: " + str(CMPS128HW3Settings.localIPPort))

        localIP = os.getenv('IPPORT').split(":")[0]
        logging.debug("Value of local IP: " + str(localIP))

        localPort = os.getenv('IPPORT').split(":")[1]
        logging.debug("Value of local port: " + str(localPort))

        # Number of total nodes
        numOfNodes = len(os.getenv('VIEW').split(","))
        logging.debug("Number of nodes: " + str(numOfNodes))

        # Number of replicas determined by client
        numOfReplicas = int(os.getenv('K'))
        logging.info("Number of replicas: " + str(numOfReplicas))

        # All the nodes stored in the initial "VIEW" list
        viewList = os.getenv('VIEW').split(",")
        logging.debug("List of all IP:PORT values in the VIEW: " + str(viewList))

        # Simple loop to assign IP:Port values to each of the nodes, and append the nodes to the global
        # nodesList
        for i in range(numOfNodes):
            # Declare a node "holder", pointing at a fresh node to be stored in the global replica list
            singleNode = CMPS128HW3Node()
            # Iterating through the VIEW list, another "holder" variable for a specific "IP:PORT" value
            singleIPPort = viewList[i]
            # Set the IPPort and other values that are needed
            singleNode.set_IPPort(singleIPPort)
            # Append this node to the entire global list of nodes in the KVS
            CMPS128HW3Settings.nodesList.append(singleNode)


        # Pass the number of nodes and replicas to subroutine to determine replicas and proxies (if any)
        self.delegate_replicas_and_proxies(numOfNodes, numOfReplicas)

        # Add the appropriate resources and run the application
        # api.add_resource(CMPS128HW3KVSReplica, '/kv-store/<val>')
        api.add_resource(CMPS128HW3KVSNodeDetails, '/kv-store/get_node_details')
        api.add_resource(CMPS128HW3KVSGetAllReplicas, '/kv-store/get_all_replicas')
        api.add_resource(CMPS128HW3KVSUpdateView, '/kv-store/update_view?type=<type>')

        app.run(host='0.0.0.0', port=str(localPort))

    """
        Should the number of nodes be greater than the number of replicas, we will assign roles to replicas
        & proxies (note that this is the initial initialization only).

        Here, if the number of nodes is greater than or equal to the number of replicas, then we delegate which
        nodes are proxies and which are replicas. In this instance, we will delegate the first k nodes as replicas,
        and the rest will be proxies.

        Though, if the number of nodes is less than the number of proxies, we assume all current nodes are replicas
        and we perform "degraded mode."
    """
    def delegate_replicas_and_proxies(self, numOfNodes, numOfReplicas):
        if numOfNodes >= numOfReplicas:
            # For the entire list, print out each node value and then assign the first k nodes as replicas in a
            # dictionary. The upper bound here will be number of replicas.
            for i in range(numOfReplicas):
                singleNode = CMPS128HW3Settings.nodesList[i]
                singleNode.set_replica()
                logging.debug("Role of " + str(singleNode.get_IPPort()) + ": " + singleNode.get_role())
            # For the entire list, print out each node value and then assign the first [k+1]...[number of nodes] as
            # replicas in a dictionary. The upper bound here will be number of total nodes, and the lower bound will be
            # the number of replicas.
            for i in range(numOfReplicas, numOfNodes):
                singleNode = CMPS128HW3Settings.nodesList[i]
                singleNode.set_proxy()
                logging.debug("Role of " + str(singleNode.get_IPPort()) + ": " + singleNode.get_role())
        else:
            # For the entire list, print out each node value and then assign all the nodes as replicas in a
            # dictionary. The upper bound here will be number of total nodes.
            for i in range(numOfNodes):
                singleNode = CMPS128HW3Settings.nodesList[i]
                singleNode.set_replica()
                logging.debug("Role of " + str(singleNode.get_IPPort()) + ": " + singleNode.get_role())

# Initiate a new thread for the method
if __name__ == '__main__':
    try:
        # Setting root logging level to DEBUG
        logging.getLogger().setLevel(logging.DEBUG)

        # Initiate the threads
        settings_thread = threading.Thread(target=CMPS128HW3Settings.CMPS128HW3Settings)
        settings_thread.start()
        main_thread = threading.Thread(target=CMPS128HW3Main)
        main_thread.start()
    except Exception as e:
        logging.error(e)