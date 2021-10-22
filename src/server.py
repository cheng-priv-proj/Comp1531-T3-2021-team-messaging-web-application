from re import T
import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config

from src.user import user_profile_v1, users_all_v1, user_setname_v1, user_setemail_v1, user_sethandle_v1
from src.channels import channels_listall_v1, channels_list_v1, channels_create_v1
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_create_v1, dm_messages_v1
from src.channel import channel_invite_v1, channel_messages_v1, channel_details_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1, channel_join_v1
from src.message import message_send_v1, message_senddm_v1, message_remove_v1, message_edit_v1

from src.data_store import data_store
from src.error import InputError
from src.other import clear_v1
from src.other import token_to_auth_id
from src.config import SECRET

from src.admin import admin_userpermission_change_v1
from src.admin import admin_user_remove_v1

import jwt 

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
    
    token = jwt.encode({
                'auth_user_id': auth_id,
                'token_count': len(data_store.get_u_ids_from_token_dict())
                },
                 SECRET, algorithm='HS256')

    data_store.insert_token(token, auth_id)

    return {'token': token, 'auth_user_id': auth_id}

# Auth login
@APP.route('/auth/login/v2', methods = ['POST'])
def login_ep():

    '''
    auth/login/v2
    POST

    Given a registered user's email and password, returns their `token` value.

    Parameters:{ email, password }
    
    Return Type:{ token, auth_user_id }

    exceptions:
    InputError when any of:
      
        email entered does not belong to a user
        password is not correct
    
    '''
    login_details = request.get_json(force = True)

    email = login_details.get('email')
    password = login_details.get('password')

    return auth_login_v1(email, password)

# Auth logout
@APP.route('/auth/logout/v1', methods = ['POST'])
def logout_endpt():
    '''
    Given a valid token, invalidates it for future use
    
    Arguments:
        token (str)
        
    Exceptions:
        AccessError - Token is invalid
        
    Returns nothing when successful
    '''
    token = request.get_json(force = True).get('token')
    token_to_auth_id(token)
    return auth_logout_v1(token)


###################### Channels ######################
# Channel create
@APP.route('/channels/create/v2', methods = ['POST'])
def channel_create_ep():

    '''
    channels/create/v2
    POST
    Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins the channel.

    Parameters:{ token, name, is_public }
    
    Return Type:{ channel_id }

    exceptions:
    InputError when:
      
        length of name is less than 1 or more than 20 characters
    '''
    create_details = request.get_json(force = True)

    token = create_details.get('token')
    auth_user_id = token_to_auth_id(token)
    name = create_details.get('name')
    is_public = create_details.get('is_public')


    channel_id_dict = channels_create_v1(auth_user_id, name, is_public)
    channel_id = channel_id_dict.get('channel_id')

    return {'channel_id': channel_id}

###################### Channel ######################
# Channel Invite 
@APP.route('/channel/invite/v2', methods = ['POST'])
def channel_invite_ep():

    '''
    channel/invite/v2
    POST

    Invites a user with ID u_id to join a channel with ID channel_id. 
    Once invited, the user is added to the channel immediately. 
    In both public and private channels, all members are able to invite users.
    
    Parameters:{ token, channel_id, u_id }
    
    Return Type:{}

    InputError when any of:
      
        channel_id does not refer to a valid channel
        u_id does not refer to a valid user
        u_id refers to a user who is already a member of the channel
      
      AccessError when:
      
        channel_id is valid and the authorised user is not a member of the channel
    '''
    invite_details = request.get_json(force = True)

    token = invite_details.get('token')
    auth_user_id = token_to_auth_id(token)
    channel_id = invite_details.get('channel_id')
    u_id = invite_details.get('u_id')

    channel_invite_v1(auth_user_id, channel_id, u_id)
    return {}

# Channel messages 
@APP.route('/channel/messages/v2', methods = ['GET'])
def channel_messages_ep():
    '''
    channel/messages/v2

    GET

    Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the channel. 
    This function returns a new index "end" which is the value of "start + 50", or, if this function has returned the least recent messages in the channel, 
    returns -1 in "end" to indicate there are no more messages to load after this return.

    Parameters:{ token, channel_id, start }

    Return Type:{ messages, start, end }
    
    InputError when any of:
      
        channel_id does not refer to a valid channel
        start is greater than the total number of messages in the channel
      
      AccessError when:
      
        channel_id is valid and the authorised user is not a member of the channel
    '''

    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    return channel_messages_v1(auth_user_id, int(channel_id), int(start))

@APP.route('/channel/leave/v1', methods = ['POST'])
def channel_leave_endpt():
    '''
    Given a channel with ID channel_id that the authorised user is a member of,
    remove them as a member of the channel.

    Arguments:
        token           (str)   - unique user token
        channel_id      (int)   - unique channel id

    Exceptions:
        TypeError   - occurs when token is not a str
        TypeError   - occurs when channel_id is not a int
        AccessError - occurs when token is invalid
        InputError  - occurs when channel_id is invalid
        AccessError - occurs when channel_id is valid and the authorised user is
                      not a member of the channel

    Return value:
        Returns nothing on success
    '''

    leave_input = request.get_json(force = True)

    token = leave_input.get('token')
    auth_user_id = token_to_auth_id(token)
    channel_id = leave_input.get('channel_id')

    return channel_leave_v1(auth_user_id, channel_id)

@APP.route('/channels/list/v2', methods = ['GET'])
def channel_list_endpt():
    '''
    channels/list/v2
    Provide a list of all channels (and their associated details) that the authorised user is part of.

    GET

    Parameters:{ token }
    
    Return Type:{ channels }
    '''

    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)

    return channels_list_v1(auth_user_id)

@APP.route('/channels/listall/v2', methods = ['GET'])
def list_all_endpt():
    '''
    channels/listall/v2
    Provide a list of all channels, including private channels, (and their associated details)

    GET

    Parameters:{ token }
    
    Return Type:
    
    '''

    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)

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
    auth_id = token_to_auth_id(token)
    channel_id = join_details['channel_id']
    channel_join_v1(auth_id, channel_id)
    
    return {}


@APP.route("/channel/details/v2", methods=['GET'])
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

    token = request.args.get('token')
    auth_id = token_to_auth_id(token)
    channel_id = request.args.get('channel_id')


    return channel_details_v1(auth_id, int(channel_id))

################################ DM #########################################

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_endpt():
    '''
    Create a DM an invite a list of users to that dm

    Methods:
        Post

    Arguments:
        token           (int)   - unique user token
        u_ids           (int)   - list of unique user tokens

    Exceptions:
        AccessError - occurs when token is inavlid
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when u_id is not a list
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when invalid u_id in u_ids

    Return value:
        Returns {dm_id} on success
    '''
    request_data = request.get_json(force = True)
    auth_user_id = token_to_auth_id(request_data['token'])
    u_ids = request_data['u_ids']

    return_dict = dm_create_v1(auth_user_id, u_ids)
    return return_dict

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_endpt():
    '''
    Given a DM with ID dm_id that the authorised user is a member of, 
    provide basic details about the DM.

    Methods:
        Get

    Arguments:
        token           (int)   - unique user token
        dm_id           (int)   - unique dm id

    Exceptions:
        AccessError - occurs when token is invalid
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when dm_id is not an int
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when dm_id does not refer to a valid DM
        AccessError - occurs when dm_id is valid and the authorised user is not a member of the DM

    Return value:
        Returns {name, members} on success
    '''

    
    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)
    dm_id = request.args.get('dm_id')

    return_dict = dm_details_v1(auth_user_id, int(dm_id))
    return return_dict

@APP.route('/channel/addowner/v1', methods=['POST'])
def channel_addowner_endpt():
    '''
    Make user with user id u_id an owner of the channel.

    Arguments:
        token           (int)   - unique user token
        channel_id      (int)   - unique channel id
        u_id            (int)   - unique user id

    Exceptions:
        AccessError - occurs when token is invalid
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when channel_id is invalid
        AccessError - occurs when channel_id is valid and the authorised user does not have owner permissions in the channel
        InputError  - occurs when u_id does not refer to a valid user
        InputError  - occurs when u_id refers to a user who is not a member of the channel
        InputError  - occurs when u_id refers to a user who is already an owner of the channel

    Returns:
        Returns nothing on success
    '''
    
    request_data = request.get_json()
    token = request_data['token']
    auth_id = token_to_auth_id(token)
    channel_id = request_data.get('channel_id')
    u_id = request_data.get('u_id')

    return channel_addowner_v1(auth_id, channel_id, u_id)


@APP.route('/channel/removeowner/v1', methods=['POST'])
def channel_removeowner_endpt():
    '''
    Remove user with user id u_id as an owner of the channel.

    Arguments:
        token           (str)   - authorised user token
        channel_id      (int)   - unique channel id
        u_id            (int)   - unique user id

    Exceptions:
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when channel_id is invalid
        AccessError - occurs when channel_id is valid and the authorised user does not have owner permissions in the channel
        InputError  - occurs when u_id does not refer to a valid user
        InputError  - occurs when u_id refers to a user who is not an owner of the channel
        InputError  - occurs when u_id refers to a user who is currently the only owner of the channel

    Returns:
        Returns nothing on success
    '''
    
    request_data = request.get_json()
    token = request_data['token']
    auth_id = token_to_auth_id(token)
    channel_id = request_data.get('channel_id')
    u_id = request_data.get('u_id')

    return channel_removeowner_v1(auth_id, channel_id, u_id)

################## User ###################################
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile_ep():
    '''
    For a valid user, returns information about their user_id, email, 
    first name, last name, and handle

    Arguments:
        token           (str)   - authorised user id
        u_id            (int)   - unique id

    Exceptions:
        AccessError - occurs when token is invalid
        InputError  - occurs when u_id is invalid

    Return value:
        Returns user on success
    '''

    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)
    u_id = request.args.get('u_id')

    user_details = user_profile_v1(auth_user_id, int(u_id))
    return user_details

@APP.route("/users/all/v1", methods=['GET'])
def users_all_ep():
    
    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)

    return users_all_v1(auth_user_id)

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname_ep():
    '''
    Update the authorised user's first and last name

    Arguments:
        token           (str)   - valid token
        name_first      (str)   - string
        name_last       (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when name_first, name_last are not between 1 and 50 characters

    Return value:
        Returns nothing on success
    '''
    request_data = request.get_json()
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)

    name_first = request_data.get('name_first')
    name_last = request_data.get('name_last')

    user_setname_v1(auth_user_id, name_first, name_last)
    return {}

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_endpt():
    '''
    dm/leave/v1
    Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist if this happens. 
    This does not update the name of the DM.

    POST

    Parameters:
        { token, dm_id }
    Return Type:
        {}

    InputError when:
      
        dm_id does not refer to a valid DM
      
    AccessError when:
      
        dm_id is valid and the authorised user is not a member of the DM

    '''
    req_details = request.get_json(force = True)

    token = req_details.get('token')
    
    auth_user_id = token_to_auth_id(token)
    dm_id = req_details['dm_id']

    dm_leave_v1(auth_user_id, dm_id)

    return {}

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_endpt():
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

    Arguments:
        token       (string)    - unique user token
        dm_id       (int)       - refers to a dm

    Exceptions:
        AccessError - Occurs when token is invalid
        InputError  - Occurs when dm_id does refer to a valid DM
        AccessError - Occurs when dm_id is valid but auth_id is not a creator of the DM

    Return Value:
        Returns nothing on success
    '''
    request_data = request.get_json(force = True)
    auth_id = token_to_auth_id(request_data['token'])
    dm_id = request_data['dm_id']
    
    return dm_remove_v1(auth_id, dm_id)

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_ep():
    '''
        Returns the list of DMs that the user is a member of.

        Arguments:
            token       (string)    - unique user token

        Exceptions:
            AccessError - Occurs when token is invalid

        Return Value:
            Returns nothing on success
    '''

    token = request.args.get('token')
    auth_user_id = token_to_auth_id(token)

    dm_list = dm_list_v1(auth_user_id)

    return dm_list
    
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail_ep():
    '''
    Update the authorised user's email address

    Arguments:
        token           (str)   - valid token
        email           (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when email is not valid

    Return value:
        Returns nothing on success
    '''

    request_data = request.get_json()
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    email = request_data.get('email')

    user_setemail_v1(auth_user_id, email)
    return {}

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle_ep():
    '''
    Update the authorised user's handle

    Arguments:
        token           (str)   - valid token
        handle          (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when handle is invalid

    Return value:
        Returns nothing on success
    '''

    request_data = request.get_json()
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    handle = request_data.get('handle_str')

    user_sethandle_v1(auth_user_id, handle)
    return {}

@APP.route("/message/send/v1", methods=['POST'])
def message_send_endpt():
    '''
    Send a message from the authorised user to the channel specified by channel_id

    Arguments:
        token           (str)   - unique user token
        channel_id      (int)   - unique channel id
        message         (str)   - message string

    Exceptions:
        AccessError - occurs when token is invalid
        TypeError   - occurs when auth_user_id, channel_id are not ints
        TypeError   - occurs when message is not a str
        AccessError - occurs when auth_user_id is invalid
        AccessError - occurs when channel_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success
    '''

    request_data = request.get_json(force = True)
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    channel_id = request_data['channel_id']
    message = request_data['message']

    return_dict = message_send_v1(auth_user_id, channel_id, message)
    return return_dict

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_endpt():
    
    token = request.args.get('token')
    auth_id = token_to_auth_id(token)
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')

    return dm_messages_v1(auth_id, int(dm_id), int(start))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_endpt():
    '''
    Send a message from the authorised user to the dm specified by dm_id

    Arguments:
        token           (str)   - unique user token
        dm_id           (int)   - unique dm id
        message         (str)   - message string

    Exceptions:
        AccessError - occurs when token is invalid
        TypeError   - occurs when auth_user_id, dm_id are not ints
        TypeError   - occurs when message is not a str
        AccessError - occurs when auth_user_id is invalid
        AccessError - occurs when dm_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success
    '''

    request_data = request.get_json(force = True)
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    dm_id = request_data['dm_id']
    message = request_data['message']

    return_dict = message_senddm_v1(auth_user_id, dm_id, message)
    return return_dict

@APP.route("/message/edit/v1", methods=['PUT'])

def message_edit_endpt():
    request_data = request.get_json(force = True)
    message_id = request_data['message_id']
    message = request_data['message']
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    return message_edit_v1(auth_user_id, message_id, message)

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_endpt():
    request_data = request.get_json(force = True)
    message_id = request_data['message_id']
    token = request_data['token']
    auth_user_id = token_to_auth_id(token)
    return message_remove_v1(auth_user_id, message_id)


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change_v1_endpt():

    request_data = request.get_json()
    token = request_data['token']
    auth_id = token_to_auth_id(token)
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']

    admin_userpermission_change_v1(auth_id, u_id, permission_id)

    return {}

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove_v1_endpt():
    request_data = request.get_json()
    token = request_data['token']
    auth_id = token_to_auth_id(token)
    u_id = request_data['u_id']

    admin_user_remove_v1(auth_id, u_id)

    return{}



#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
    