from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import *

'''
Adds another user to a channel that the auth_user is a member of.

Arguments:
    auth_user_id    (int)   - authorised user id (inviter)
    channel_id      (int)   - unique channel id
    u_id            (int)   - user id (invitee)

Exceptions:
    TypeError   - occurs when auth_user_id, channel_id, u_id are not ints
    AccessError - occurs when auth_id is invalid
    AccessError - occurs when channel_id is valid but the authorised user is not
                  a member of the channel
    InputError  - occurs when channel_id is invalid
    InputError  - occurs when the u_id is invalid
    InputError  - occurs when the u_id refers to a user who is already a member
                  of the channel

Return value:
    Returns nothing on success
'''
def channel_invite_v1(auth_user_id, channel_id, u_id):

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(u_id, int)

    # checking if auth_id is valid
    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError('Invalid auth_user_id')

    # pull info from datastore
    channels = data_store.get_channels_from_channel_id_dict()
    
    channel_details = channels.get(channel_id)

    # Checking if channel_id is valid
    if channel_id not in channels:
        raise InputError

    # Checks whether invitor is a member of channel
    inviter_u_id = data_store.get_u_id_from_auth_dict().get(auth_user_id)
    if not data_store.check_user_is_member_of_channel(channel_id, inviter_u_id):
        raise AccessError

    # Checking if invitee_u_id is valid 
    users = data_store.get_users_from_u_id_dict()
    if u_id not in users:
        raise InputError
    
    # checking if invitee is already a member of channel
    if data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise InputError
    
    channel_details.get('all_members').append(users.get(u_id))

    return {}

'''
Returns the details of a given channel that an authorised user has access to.

Arguments:
    auth_user_id    (int)   - authorised user id
    channel_id      (int)   - unique channel id

Exceptions:
    TypeError   - occurs when auth_user_id, channel_id are not ints
    AccessError - occurs when auth_id is invalid
    InputError  - occurs when channel_id is invalid
    InputError  - 

Return value:
    Returns nothing on success
'''
def channel_details_v1(auth_user_id, channel_id):

    check_type(auth_user_id, int)
    check_type(channel_id, int)

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError
        
    channels = data_store.get_channels_from_channel_id_dict()
    if channel_id not in channels:
        raise InputError
    
    channel = channels.get(channel_id)
        
    u_id = data_store.get_u_id_from_auth_dict().get(auth_user_id)

    if not data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise AccessError

    channel = channels.get(channel_id)

    return channel

'''
Returns a list of messages between index 'start' and up to 'start' + 50 from a
given channel that the authorised user has access to. Additionally returns
'start', and 'end' = 'start' + 50
t

Arguments:
    auth_user_id    (int)   - authorised user id
    channel_id      (int)   - unique channel id
    start           (int)   - message index (most recent message has index 0)

Exceptions:
    TypeError   - occurs when auth_user_id, channel_id are not ints
    AccessError - occurs when auth_id is invalid
    InputError  - occurs when channel_id is invalid
    InputError  - occurs when start is negative
    InputError  - occurs when start is greater than the total number of messages
                  in the channel

Return value:
    Returns { messages, start, end } on success
    Returns { messages, start, -1 } if the function has returned the least
    recent message
'''
def channel_messages_v1(auth_user_id, channel_id, start):

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(start, int)

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError

    # ASSUMPTION: negative start index causes an InputError exception
    if start < 0:
        raise InputError('start is a negative integer')

    # Checking if the channel id exists
    channels = data_store.get_channels_from_channel_id_dict()

    if channel_id not in channels:
        raise InputError('channel_id does not refer to a valid channel')

    channel = channels.get(channel_id)

    # Checking that auth_id exists in channel
    u_id_from_auth = data_store.get_u_id_from_auth_dict().get(auth_user_id)
    if not data_store.check_user_is_member_of_channel(channel_id, u_id_from_auth):
        raise AccessError('the authorised user is not a member of the channel')

    messages = data_store.get_messages_from_channel_id_dict().get(channel_id)
    no_of_messages = len(messages)

    end = start + 50

    if start > no_of_messages:
        raise InputError('start is greater than the total number of messages in the channel')

    # accounts for when given empty channel and start = 0
    elif  start + 50 >= no_of_messages:
        end = -1
    
    return {
        'messages' : messages,
        'start': start,
        'end' : end
        }

'''
Adds an authorised user to a channel

Arguments:
    auth_user_id    (int)   - authorised user id
    channel_id      (int)   - unique channel id

Exceptions:
    TypeError   - occurs when auth_user_id, channel_id are not ints
    AccessError - occurs when auth_id is invalid
    InputError  - occurs when channel_id is invalid
    AccessError - occurs when channel is not public
    InputError  - occurs when user

Return value:
    Returns nothing on success
'''
def channel_join_v1(auth_user_id, channel_id):

    check_type(auth_user_id, int)
    check_type(channel_id, int)

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError

    channels = data_store.get_channels_from_channel_id_dict()

    if channel_id not in channels:
        raise InputError

    channel = channels.get(channel_id)

    u_id = data_store.get_u_id_from_auth_dict().get(auth_user_id)

    # Checking if user exists in all members
    if data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise InputError

    # Checking if channel is public
    if not channel.get('is_public'):
        raise AccessError

    user = data_store.get_user_info_from_auth_id(auth_user_id)
    channel.get('all_members').append(user)

    return {}
