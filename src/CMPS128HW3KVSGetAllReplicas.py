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
    In this file, we will return the number of replicas that are currently available in the key-value store.
    :var nodesList: The global list from CMPS128HW3
    :return: A HTTP response with the list of replicas
"""
class CMPS128HW3KVSGetAllReplicas(Resource):

    # Initialize class variables to point at global variables (for the sake of brevity)
    def __init__(self):
        self.replicaList = CMPS128HW3Settings.replicaList

    # GET method to get the list of replicas
    def get(self):
        try:
            # For each node in the global nodesList (in CMPS128HW3Main), turn each item in the list into a string
            # and append it to the local replicaList, to be turned into JSON in json_resp
            json_resp = json.dumps({
                "result":"success",
                "replicas": self.replicaList
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