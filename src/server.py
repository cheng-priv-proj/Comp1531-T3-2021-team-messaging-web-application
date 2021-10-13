import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.channel import channel_join_v1, channel_details_v1


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

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_endpt():
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.
    Parameters:
    { token, channel_id }
    
    Return Type:
    {}

    Exceptions:

      InputError when any of:
        channel_id does not refer to a valid channel
        the authorised user is already a member of the channel
      
      AccessError when:
        channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner

    '''
    
    join_details = request.get_json()
    auth_id = join_details['token']
    channel_id = join_details['channel_id']
    channel_join_v1(auth_id, channel_id)

    return {}


@APP.route("/channel/details/v2", methods=['get'])
def channel_details_endpt():
    '''
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.

    Parameters: 
    { token, channel_id }

    Return Type: 
    { name, is_public, owner_members, all_members }

    Exceptions: 
    InputError when:
        channel_id does not refer to a valid channel
    
    '''

    request_data = request.get_json()
    auth_id = request_data['token']
    channel_id = request_data['channel_id']
    return_dict = channel_details_v1(auth_id, channel_id)
    return return_dict

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
