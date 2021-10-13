import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config

from src.channel import channel_join_v1, channel_details_v1
from src.channels import channels_listall_v1, channels_list_v1

from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_invite_v1, channel_messages_v1, channel_details_v1

from src.data_store import data_store
from src.error import InputError
from src.other import clear_v1

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

###################### Auth ######################
# Auth register 
# Change to dictionary?
# Return errors?
@APP.route('/auth/register/v2', methods = ['POST'])
def register_ep():
    '''
    Given a user's first and last name, email address, and password, create a new account for them and return a new `token`.

    Parameters: { email, password, name_first, name_last }

    Return Type: { token, auth_user_id }
    
    Exceptions:

    InputError when any of:
      
        email entered is not a valid email (more in section 6.4)
        email address is already being used by another user
        length of password is less than 6 characters
        length of name_first is not between 1 and 50 characters inclusive
        length of name_last is not between 1 and 50 characters inclusive
    
    
    '''
    register_details = request.get_json(force = True)

    email = register_details.get('email')
    password = register_details.get('password')
    name_first = register_details.get('name_first')
    name_last = register_details.get('name_last')

    auth_id_dict = auth_register_v1(email, password, name_first, name_last)
    auth_id = auth_id_dict.get('auth_user_id')
    token = str(auth_id) # Change to jwt later

    data_store.insert_token(token, auth_id)

    return {'token': token, 'auth_user_id': auth_id}

# Auth login
@APP.route('/auth/login/v2', methods = ['POST'])
def login_ep():
    login_details = request.get_json(force = True)

    email = login_details.get('email')
    password = login_details.get('password')

    auth_id_dict = auth_login_v1(email, password)
    auth_id = auth_id_dict.get('auth_user_id')
    token = str(auth_id) # Change to jwt later

    return {'token': token, 'auth_user_id': auth_id}

###################### Channels ######################
# Channel create
@APP.route('/channels/create/v2', methods = ['POST'])
def channel_create_ep():
    create_details = request.get_json(force = True)

    token = create_details.get('token')
    auth_user_id = data_store.get_u_id_from_token(token) # Does it return NONE?
    name = create_details.get('name')
    is_public = create_details.get('is_public')

    print(auth_user_id)

    channel_id_dict = channels_create_v1(auth_user_id, name, is_public)
    channel_id = channel_id_dict.get('channel_id')

    return {'channel_id': channel_id}

###################### Channel ######################
# Channel Invite 
@APP.route('/channel/invite/v2', methods = ['POST'])
def channel_invite_ep():
    invite_details = request.get_json(force = True)

    token = invite_details.get('token')
    auth_user_id = data_store.get_u_id_from_token(token)
    channel_id = invite_details.get('channel_id')
    u_id = invite_details.get('u_id')

    channel_invite_v1(auth_user_id, channel_id, u_id)
    return {}

# Channel messages 
@APP.route('/channel/messages/v2', methods = ['GET'])
def channel_messages_ep():
    message_get_details = request.get_json(force = True)

    token = message_get_details.get('token')
    auth_user_id = data_store.get_u_id_from_token(token)
    channel_id = message_get_details.get('channel_id')
    start = message_get_details.get('start')

    print(channel_messages_v1(auth_user_id, channel_id, start))

    return channel_messages_v1(auth_user_id, channel_id, start)

@APP.route('/channels/list/v2', methods = ['GET'])
def channel_list_endpt():
    list_details = request.get_json(force = True)

    token = list_details.get('token')
    auth_user_id = data_store.get_u_id_from_token(token)

    return channels_list_v1(auth_user_id)



@APP.route('/channels/listall/v2', methods = ['GET'])
def list_all():
    listall_details = request.get_json(force = True)

    token = listall_details.get('token')
    auth_user_id = data_store.get_u_id_from_token(token)

    return channels_listall_v1(auth_user_id)


# Clear 
@APP.route("/clear/v1", methods = ['DELETE'])
def clear_ep():
    clear_v1()
    return {}

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
    token = join_details['token']
    auth_id = data_store.get_u_id_from_token(token)
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
    token = request_data['token']
    auth_id = data_store.get_u_id_from_token(token)
    channel_id = request_data['channel_id']

    return_dict = channel_details_v1(auth_id, channel_id)
    print(return_dict)
    return return_dict

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(debug = True, port=config.port) # Do not edit this port
