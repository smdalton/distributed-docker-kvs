"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

"""
    Global variables for the entire codebase are initialized here.
    
    Global variables
    --------------------
    :var localIPPort: The localIPPort for this specific instance in the form of IP:PORT
    :var nodesList: All the IP:PORT values for all instances that exist in the KVS, as a list
    :var nodeStatus: All the instances with their status (as a replica or a proxy), in a list
    :var replicaList: All the designated replicas (as IP:PORT values) in a list
    :var proxyList: All the designated proxies (as IP:PORT values) in a list
"""
class CMPS128HW3Settings:
    def __init__(self):
        # Global variables to be used in all modules in the codebase
        global nodeStatus
        nodeStatus = dict()

        global replicaList
        replicaList = []

        global proxyList
        proxyList = []

        global localIPPort

        global nodesList