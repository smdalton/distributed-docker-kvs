"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

import logging
import threading

from CMPS128HW3KVSNodeDetails import CMPS128HW3KVSNodeDetails
from CMPS128HW3KVSGetAllReplicas import CMPS128HW3KVSGetAllReplicas
from CMPS128HW3KVSUpdateView import CMPS128HW3KVSUpdateView
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
"""
class CMPS128HW3Main:
    """
        Initiate the application with the appropriate KVS resource, logic to see if this instance is the main instance or
        a forwarding instance.

        Global variables (as listed in the settings file)
        -----------------------------------------------------
        :var localIPPort: The localIPPort for this specific instance in the form of IP:PORT
        :var nodesList: All the IP:PORT values for all instances that exist in the KVS, as a list
        :var nodeStatus: All the instances with their status (as a replica or a proxy), in a list
        :var replicaList: All the designated replicas (as IP:PORT values) in a list
        :var proxyList: All the designated proxies (as IP:PORT values) in a list

        Local variables
        --------------------
        :var localIP: The local IP for this specific instance, by itself
        :var localPort: The local port for this specific instance, by itself
        :var numOfNodes: The number of total nodes/instances (or IP:PORT items) that exist in the KVS
        :var numOfReplicas: The number of desired instances to be replicas, as specified by the client
    """
    def __init__(self):

        # Initialize the application with the appropriate route
        app = Flask(__name__)
        api = Api(app)

        # Environment variables
        CMPS128HW3Settings.localIPPort = os.getenv('IPPORT')
        logging.debug("Value of IP:PORT: " + str(CMPS128HW3Settings.localIPPort))

        CMPS128HW3Settings.nodesList = os.getenv('VIEW').split(",")
        logging.debug("List of nodes: " + str(CMPS128HW3Settings.nodesList))

        localIP = os.getenv('IPPORT').split(":")[0]
        logging.debug("Value of local IP: " + str(localIP))

        localPort = os.getenv('IPPORT').split(":")[1]
        logging.debug("Value of local port: " + str(localPort))

        # Number of total nodes
        numOfNodes = len(CMPS128HW3Settings.nodesList)
        logging.debug("Number of nodes: " + str(numOfNodes))

        # Number of replicas determined by client
        numOfReplicas = int(os.getenv('K'))
        logging.info("Number of replicas: " + str(numOfReplicas))

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
        & proxies.

        Here, if the number of nodes is greater than or equal to the number of replicas, then we delegate which
        nodes are proxies and which are replicas. In this instance, we will delegate the first k nodes as replicas,
        and the rest will be proxies.

        Though, if the number of nodes is less than the number of proxies, we assume all current nodes are replicas
        and we perform "degraded mode."
    """
    def delegate_replicas_and_proxies(self, numOfNodes, numOfReplicas):
        if numOfNodes >= numOfReplicas:
            # For the entire list, print out each node value and then assign the first k nodes as replicas in a
            # dictionary. The upper bound here will be number of replicas. We will take the IP:PORT value as a key,
            # and the associated status (in this case, "replica"), as its value
            for i in range(numOfReplicas):
                logging.debug("Replica value: " + str(CMPS128HW3Settings.nodesList[i]))
                # Append the IP:PORT value to the replicas list
                CMPS128HW3Settings.replicaList.append(str(CMPS128HW3Settings.nodesList[i]))
                # Store the value in the nodeStatus dict as a replica
                CMPS128HW3Settings.nodeStatus[CMPS128HW3Settings.nodesList[i]] = "replica"
            # For the entire list, print out each node value and then assign the first [k+1]...[number of nodes] as
            # replicas in a dictionary. The upper bound here will be number of total nodes, and the lower bound will be
            # the number of replicas. We will take the IP:PORT value as a key, and the associated status
            # (in this case, "proxy") as its value
            for i in range(numOfReplicas, numOfNodes):
                logging.debug("Proxy value: " + str(CMPS128HW3Settings.nodesList[i]))
                # Append the IP:PORT value to the proxy list
                CMPS128HW3Settings.proxyList.append(str(CMPS128HW3Settings.nodesList[i]))
                # Store the value in the nodeStatus dict as a proxy
                CMPS128HW3Settings.nodeStatus[CMPS128HW3Settings.nodesList[i]] = "proxy"
        else:
            # For the entire list, print out each node value and then assign all the nodes as replicas in a
            # dictionary. The upper bound here will be number of total nodes. We will take the IP:PORT value as a key,
            # and the associated status (in this case, "replica"), as its value
            for i in range(numOfNodes):
                logging.debug("Replica value: " + str(CMPS128HW3Settings.nodesList[i]))
                # Append the IP:PORT value to the replicas list
                CMPS128HW3Settings.replicaList.append(str(CMPS128HW3Settings.nodesList[i]))
                # Store the value in the nodeStatus dict as a replica
                CMPS128HW3Settings.nodeStatus[CMPS128HW3Settings.nodesList[i]] = "replica"

# Initiate a new thread for the method
if __name__ == '__main__':
    try:
        # Setting root logging level to DEBUG
        logging.getLogger().setLevel(logging.DEBUG)

        # Initiate the threads
        settings_thread = threading.Thread(target=CMPS128HW3Settings.CMPS128HW3Settings())
        settings_thread.start()
        main_thread = threading.Thread(target=CMPS128HW3Main)
        main_thread.start()
    except Exception as e:
        logging.error(e)