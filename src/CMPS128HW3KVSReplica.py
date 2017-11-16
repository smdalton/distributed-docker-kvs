"""
    Author: Cristian Gonzales
    Created for UCSC undergrad course CMPS 128, Fall 2017
"""

from flask_restful import Resource
from flask_restful import abort
from flask import request
from flask import Response
from datetime import datetime
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import json
import logging
import re
import threading

"""
    Initialize an empty dictionary.
    :var KVSDict: The global dictionary that will serve as our KVS
"""
global KVSDict
KVSDict = dict()
gossipTimer = 5;



def gossip():
    try:
        print ("Gossiping")
        
    except Exception as e:
        logging.error(e)
        abort(400, message=str(e))
        

sched = BackgroundScheduler(daemon=True)
sched.add_job(gossip,'interval',seconds=3)
sched.start()
        
"""
    Class that implements the KVS. Refer to the README for specifications and functional guarantees.
"""
# TODO: Clean up *all* logic in this class
class CMPS128HW3KVSReplica(Resource):
    


            

    """
       GET request
       :return: HTTP response
    """

    
    def get(self, key):
        try:
            # If the requested argument is in the dictionary, then return a sucessful message with the last stored
            # value. If not, then return a 404 error message
            logging.info("Value of key: " + str(KVSDict.get(key)))
            print(type(KVSDict[key]))

            if key in KVSDict:
                logging.debug(key)
                # val = KVSDict[key]['val']
                # print("val --->", val)
                json_resp = json.dumps(
                    {
                        'result':'Success',
                        'value': KVSDict[key]['val']
                    }
                )
                # Return the response
                return Response(
                    json_resp,
                    status=200,
                    mimetype='application/json'
                )
            else:
                json_resp = json.dumps(
                    {
                        'result': 'Error',
                        'msg': 'Key does not exist'
                    }
                )
                # Return the response
                return Response(
                    json_resp,
                    status=404,
                    mimetype='application/json'
                )
        except Exception as e:
            logging.error(e)
            abort(400, message=str(e))

    """
        PUT request
        :return: HTTP response
    """
    def put(self, key):
        try:
            
            # self.gossip()
            logging.debug(key)

            # Conditional to check if the input value is nothing or if there are just no arguments
            if request.form['val'] == '' or len(request.form['val']) == None:
                json_resp = json.dumps(
                    {
                        'result': 'Error',
                        'msg': 'No value provided'
                    }
                )
                return Response(
                    json_resp,
                    status=403,
                    mimetype='application/json'
                )

            # Conditional to check if the key is too long (> 200 chars)
            logging.debug("Size of key: " + str(len(key)))
            if len(key) > 200:
                json_resp = json.dumps(
                    {
                        'result': 'Error',
                        'msg': 'Key not valid'
                    }
                )
                return Response(
                    json_resp,
                    status=403,
                    mimetype='application/json'
                )

            # Conditional to check if input is greater than 1MB
            logging.debug("Size of val: " + str(len(request.form['val'])))

            if len(request.form['val']) > 1000000:
                json_resp = json.dumps(
                    {
                        'result': 'Error',
                        'msg': 'Object too large'
                    }
                )
                return Response(
                    json_resp,
                    status=404,
                    mimetype='application/json'
                )
            # Conditional to check if the input contains invalid characters outside of [a-zA-Z0-9_]
            if not re.compile('[A-Za-z0-9_]').findall(key):
                json_resp = json.dumps(
                    {
                        'result': 'Error',
                        'msg': 'Key not valid'
                    }
                )
                return Response(
                    json_resp,
                    status=404,
                    mimetype='application/json'
                )

            # If the value is in the dictionary, then replace the value of the existing key with a new value
            # Else, make a new key-val pair in the dict if the key does not exist
            if key in KVSDict:
                # Replace the key-val pair in the dict with the new requested value
                # Precondition: the key must already exist in the dict
                logging.debug(request.form['val'])
                KVSDict[key]['val'] = request.form['val']
                KVSDict[key]['clock'] = KVSDict[key]['clock'] + 1
                KVSDict[key]['timestamp'] = str(datetime.now())
                json_resp = json.dumps(
                    {
                        'replaced': 'True',
                        'msg': 'Value of existing key replaced'
                    }
                )
                # Return the response
                return Response(
                    json_resp,
                    status=200,
                    mimetype='application/json'
                )
            elif key not in KVSDict:
                logging.debug(request.form['val'])
                # Add the key-val pair to the dictionary
                KVSDict["123"] = {'val': 456}
                print("CHECK THIS OUT ", KVSDict["123"]['val'])
                newVal = {
                    'val': request.form['val'],
                    'clock': 0,
                    'timestamp': str(datetime.now())
                }

                KVSDict[key] = newVal

                #KVSDict[key] = request.form['val'] old way


                json_resp = json.dumps(
                    {
                        'replaced': 'False',
                        'msg': 'New key created'
                    }
                )
                #logging.debug("Value in dict: " + KVSDict[key])
                # Return the response
                return Response(
                    json_resp,
                    status=201,
                    mimetype='application/json'
                )

        except Exception as e:
            logging.error(e)
            abort(400, message=str(e))
            