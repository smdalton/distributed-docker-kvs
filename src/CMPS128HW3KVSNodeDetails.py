"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

from flask_restful import Resource
from flask_restful import abort
from flask import Response

import json

import logging

import CMPS128HW3Settings

"""
    In this file, this is a resource that will check if this instance is a forwarding instance or a replica.
    :var localIPPort: This instance's local IP and port, to be checked against the dictionary with all the IP:PORT
        keys and their associated statuses. This is global, as declared in CMPS128HW3Main
    :var nodeStatus: The dictionary that contains all the IP:PORT values and their associated statuses (either 
        they are replicas, or they are proxies).
    :return: An HTTP response
"""
class CMPS128HW3KVSNodeDetails(Resource):

    # Initialize class variables to point at global variables (for the sake of brevity)
    def __init__(self):
        self.nodeStatus = CMPS128HW3Settings.nodeStatus
        self.localIPPort = CMPS128HW3Settings.localIPPort

    # Get method to see if current instance is a replica
    def get(self):
        try:
            # If the IP:PORT value is a replica, then we will check its associated key. If it isn't then we return the
            # appropriate response.
            if self.nodeStatus[self.localIPPort] == "replica":
                json_resp = json.dumps({
                    "result": "success",
                    "replica": "Yes"
                })
            else:
                json_resp = json.dumps({
                    "result": "success",
                    "replica": "No"
                })
            # Return the response as JSON
            return Response(
                json_resp,
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            logging.error(e)
            abort(400, message=str(e))