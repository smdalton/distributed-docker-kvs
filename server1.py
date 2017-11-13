import sys
from flask import Flask, abort, request
import json
from flask import Response
import logging
import re
global this_server

app = Flask(__name__)
# from kvs_api import kvs_api

# state object for this_server's identifying information


class Node(object):
    number_of_replicas = 0
    view_node_list = []
    my_ip = ''
    my_port= ''
    my_role=''
    kvs = {}
    causal_payload = {}
    up_down = []

    def __init__(self, env_vars):
        # env_vars is sys.argv
        self.number_of_replicas = env_vars[1]
        # list of all ip:port in the view ['ip1:port1', 'ip2:port2',... etc]
        self.view_node_list = env_vars[2].split(',')
        self.my_ip = env_vars[3].split(':')[0]
        self.my_port = env_vars[3].split(':')[1]
        self.my_role = 'replica' # to start

    def my_identity(self):
        return this_server.my_ip + ":" + this_server.my_port

    #def update_payload(self):




# state object for this node
this_server = Node(sys.argv)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
    func()


# necessary for remote start/stop
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down \n'


@app.route('/kv-store/<val>', methods=['PUT', 'GET'])
def put_in_kvs(val):
    kvs_dict = this_server.kvs
    if request.method == 'PUT':
        print('got a put request')
        
        try:
            logging.debug(val)

            # Conditional to check if the input value is nothing or if there are just no arguments
            if request.form['val'] == '' or len(request.form['val']) == 0:
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
            logging.debug("Size of key: " + str(len(val)))
            if len(val) > 200:
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
            if not re.compile('[A-Za-z0-9_]').findall(val):
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
            if val in kvs_dict:
                # Replace the key-val pair in the dict with the new requested value
                # Precondition: the key must already exist in the dict
                logging.debug(request.form['val'])
                kvs_dict[val] = request.form['val']
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
            elif val not in kvs_dict:
                logging.debug(request.form['val'])
                # Add the key-val pair to the dictionary
                kvs_dict[val] = request.form['val']
                json_resp = json.dumps(
                    {
                        'replaced': 'False',
                        'msg': 'New key created'
                    }
                )
                logging.debug("Value in dict: " + kvs_dict[val])
                # Return the response
                return Response(
                    json_resp,
                    status=201,
                    mimetype='application/json'
                )

        except Exception as e:
            logging.error(e)
            abort(400, message=str(e))

    elif request.method == 'GET':
        try:
            # If the requested argument is in the dictionary, then return a sucessful message with the last stored
            # value. If not, then return a 404 error message
            logging.info("Value of key: " + str(kvs_dict.get(val)))

            if val in kvs_dict:
                logging.debug(val)
                json_resp = json.dumps(
                    {
                        'result':'Success',
                        'value': kvs_dict[val]
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

    else:
        return 'fall through error kv-store/<val>'


@app.route('/kv-store/update_view', methods=['PUT'])
def update_view():
    print(request.form)
    if request.form['type'] == 'add':
        # update the view list with a new server identity
        this_server.view_node_list.append(request.form['ip_port'])
        #this_server.update_state() #update state will
        json_resp = json.dumps({
            "msg":"success",
            "node_id": this_server.my_identity(),
            "number_of_nodes": len(this_server.view_node_list),
            "all servers": this_server.view_node_list,
        })
        return Response(
            json_resp,
            status=200,
            mimetype='application/json'
        )
    elif request.form['type'] == 'remove':
        this_server.view_node_list.remove(request.form['ip_port'])
        json_resp = json.dumps({
            "msg":"success",
            "node_id": this_server.my_identity(),
            "number_of_nodes": len(this_server.view_node_list),
            "all servers": this_server.view_node_list,
        })
        return Response(
            json_resp,
            status=200,
            mimetype='application/json'
        )
    else:
        return Response(
            json.dumps({'update_view':'fall through no match'})
        )


@app.route('/server_name',methods=['GET'])
def server_name():
    try:
        json_resp = json.dumps(
            {
                'result' :'Success',
                'value'  :'Server1',
                'ip:port': this_server.my_ip + ':' + this_server.my_port,
                'View'   : this_server.view_node_list
            }
        )
        return Response(
            json_resp,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logging.error(e)
        abort(400, message=str(e))


if __name__ == '__main__':
    app.run(host=this_server.my_ip, port=this_server.my_port)
