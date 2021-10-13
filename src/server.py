import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.channels import channels_listall_v1, channels_list_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


# THIS IS TEMPORARY
    # Considers auth_id to be the same as token.
    # When a function that converts token to auth_id made, replace this. 
@APP.route("channels/list/v2", methods=['GET'])
def channel_list_endpt():
    '''
    Provide a list of all channels (and their associated details) that the authorised user is part of.

    Parameters: 
    { token }

    Return Type: 
    { channels }

    Exceptions: N/A
    '''

    recieved_token = request.get_json()

    # THIS IS TEMPORARY
    # Considers auth_id to be the same as token.
    # When a function that converts token to auth_id made, replace this.  
    auth_id = recieved_token['token']

    return channels_list_v1(auth_id)

# THIS IS TEMPORARY
    # Considers auth_id to be the same as token.
    # When a function that converts token to auth_id made, replace this. 

@APP.route("channels/listall/v2", methods=['GET'])
def channel_list_endpt():
    '''
    Provide a list of all channels, including private channels, (and their associated details)

    Parameters: 
    { token }

    Return Type: 
    { channels }

    Exceptions: N/A
    '''

    recieved_token = request.get_json()

    # THIS IS TEMPORARY
    # Considers auth_id to be the same as token.
    # When a function that converts token to auth_id made, replace this.  
    auth_id = recieved_token['token']

    return channels_listall_v1(auth_id)



#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
