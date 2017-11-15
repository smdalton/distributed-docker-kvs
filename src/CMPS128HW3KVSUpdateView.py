"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

from flask_restful import Resource
from flask_restful import abort
from flask import Response
from flask import request

import json

import logging

import CMPS128HW3Settings

"""
    In this file, this is a resource to perform a PUT request to update the view (add or remove nodes).
    
    :return: An HTTP response
"""
class CMPS128HW3KVSUpdateView(Resource):

    """
        PUT request to add or delete a node to the network, and reconfigure the replicas and proxies such that we
        account for the new node, if it is to stay a replica or be a proxy based on the prerequisite for degraded mode
    """
    def put(self, type):
        try:
            # The new node as an IP:PORT value
            new_node_value = request.form['ip_port']
            # The PUT type (presumably, 'add' or 'remove')
            PUT_type = str(type)

            logging.debug("Type of view update: "  + PUT_type)
            logging.debug("IP:PORT value to " + PUT_type + ": " + str(new_node_value))

            # Determine if the request is to add or remove a node. Any request that deviates from this is invalid.
            if PUT_type == "add":

                # TODO: Logic to add the IP:PORT value from the appropriate lists, use logic to see how this will change
                # replica-to-proxy ratio, and return the appropriate response

                # Forming the JSON request and returning the appropriate message
                json_resp = json.dumps(
                    {
                        "msg":"success",
                        "node_id":int(new_node_value),
                        "number_of_nodes":""
                    }
                )
                return Response(
                    json_resp,
                    status=200,
                    mimetype='application/json'
                )
            elif PUT_type == "remove":

                # TODO: Logic to add the IP:PORT value from the appropriate lists, use logic to see how this will change
                # replica-to-proxy ratio, and return the appropriate response

                # Forming the JSON request and returning the appropriate message
                json_resp = json.dumps(
                    {
                        "result":"success",
                        "number_of_nodes":""
                    }
                )
                return Response(
                    json_resp,
                    status=200,
                    mimetype='application/json'
                )
            else:
                json_resp = json.dumps(
                    {
                        "result":"error",
                        "msg":"Invalid request"
                    }
                )
                return Response(
                    json_resp,
                    status=404,
                    mimetype='application/json'
                )

        except Exception as e:
            logging.error(e)
            json_resp = json.dumps(
                {
                    "result":"error",
                    "msg": str(e)
                }
            )
            return Response(
                json_resp,
                status=404,
                mimetype='application/json'
            )

    """
        Should the number of nodes be greater than the number of replicas, we will assign roles to replicas
        & proxies.

        Here, if the number of nodes is greater than or equal to the number of replicas, then we delegate which
        nodes are proxies and which are replicas. In this instance, we will delegate the first k nodes as replicas,
        and the rest will be proxies.

        Though, if the number of nodes is less than the number of proxies, we assume all current nodes are replicas
        and we perform "degraded mode."
    """
    # TODO: Clean this up and fix it so that is it suiting for this instance
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