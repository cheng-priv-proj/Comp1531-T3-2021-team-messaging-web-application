from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from copy import deepcopy

def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):

    # check for correct input types
    if type(auth_user_id) != int or type(channel_id) != int:
        raise TypeError

    channels = data_store.get_channels_from_channel_id_dict()
    
    if channel_id not in channels:
        raise InputError
    
    channel = channels.get(channel_id)

    u_ids = data_store.get_u_id_from_auth_dict()

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError
        
    u_id = u_ids.get(auth_user_id)['u_id']
    
    if not data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise AccessError

    # the 'messages' key value pair is not part of the function output
    channel_details = deepcopy(channel)
    channel_details.pop('messages')

    return channel_details

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    # CHecking valid input types: (ASSUMPTION: Type Error)
    if type(auth_user_id) != int:
        raise TypeError('Auth_user_id must be an integer')
    if type(channel_id) != int:
        raise TypeError('Channel_id must be an integer')

    channel_details = data_store.get_channels_from_channel_id_dict().get(channel_id)

    u_id_dict = data_store.get_u_id_from_auth_dict().get(auth_user_id)
    # Checking invalid auth_id: 
    if u_id_dict == None:
        raise AccessError
    # Checking if valid channel_id
    if channel_details == None:
        raise InputError
    # Checking if channel is public
    if not channel_details['is_public']:
        raise AccessError
    # Checking if user exists in all members
    if data_store.check_user_is_member_of_channel(channel_id, u_id_dict.get('u_id')):
        raise InputError

    user_info = data_store.get_user_info_from_auth_id(auth_user_id)
    channel_details['all_members'].append(user_info)

    return {
    }
