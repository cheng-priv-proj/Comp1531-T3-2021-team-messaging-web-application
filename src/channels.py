from src.data_store import *
from src.error import *

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):

    # check for correct input types
    if type(auth_user_id) != int or type(is_public) != bool:
        raise TypeError

    if len(name) < 1 or len(name) > 20 :
        raise InputError
    
    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError

    owner = data_store.get_user_info_from_auth_id(auth_user_id)

    # ASSUMPTION: channel_id starts from 0
    channels = data_store.get_channels_from_channel_id_dict()

    new_id = len(channels)
    
    data_store.insert_channel(new_id, name, is_public, [], [owner], [owner])

    return {
        'channel_id': new_id
    }
