from src.data_store import *
from src.error import *

def channels_list_v1(auth_user_id):
    u_id = data_store.get_u_id_from_auth_dict().get(auth_user_id).get('u_id')
    if type(auth_user_id) != int:
        raise TypeError('incorrect input type')

    # Check if valid id. If not then return accesserror
    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError("Invalid auth_user_id")

    # Setup Dictionary
    memberOf_channel_list = {
        'channels': [
            
        ]
    }
    
    # Get datastore 
    channels = data_store.get_channels_from_channel_id_dict()

    # Returns a dictionary of dictionaries. Loop through each key and append
    for channel_id in channels:
        if data_store.check_user_is_member_of_channel(channel_id, u_id):
            memberOf_channel_list['channels'].append( 
                {
                    'channel_id': channel_id,
                    'name': channels[channel_id]['name']
                }
            )
            print("INSIDE IF print(channel_id): ", channel_id)
            print("INSIDE IF member of channel list: ", memberOf_channel_list)
        print("print(channel_id): ",channel_id)
        print("member of channel list: ", memberOf_channel_list)
    return memberOf_channel_list

def channels_listall_v1(auth_user_id):
    if type(auth_user_id) != int:
        raise TypeError('incorrect input type')

    # Check if valid id. If not then return accesserror
    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError("Invalid auth_user_id")

    # Setup Dictionary
    all_channel_list = {
        'channels': [
            
        ]
    }
    # Get datastore 
    channels = data_store.get_channels_from_channel_id_dict()
    
    # Returns a dictionary of dictionaries. Loop through each key and append
    for channel_id in channels:
        all_channel_list['channels'].append( 
            {
                'channel_id': channel_id,
                'name': channels[channel_id]['name']
            }
        )

    return all_channel_list


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
