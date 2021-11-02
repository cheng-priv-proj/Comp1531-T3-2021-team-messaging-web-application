from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import check_type

def channels_list_v1(auth_user_id):
    '''
    Returns a list of channels that the authorised user is apart of.

    Arguments:
        auth_user_id    (int)   - authorised user id

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int

    Return value:
        Returns channels on success
    '''
    
    check_type(auth_user_id, int)
    
    channels_dict = data_store.get_channels_from_channel_id_dict()

    channels = [{
                    'channel_id': channel_id,
                    'name': channels_dict.get(channel_id).get('name')
                }
                for channel_id in channels_dict
                if data_store.is_user_member_of_channel(channel_id, auth_user_id)
               ]
            
    return { 'channels': channels }

def channels_listall_v1(auth_user_id):
    '''
    Returns a list of all channels, including private channels.

    Arguments:
        auth_user_id    (int)   - authorised user id

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int

    Return value:
        Returns channels on success
    '''
    
    check_type(auth_user_id, int)

    channels_dict = data_store.get_channels_from_channel_id_dict()
    
    # Returns a dictionary of dictionaries. Loop through each key and append
    channels = [{
                        'channel_id': channel_id,
                        'name': channels_dict.get(channel_id).get('name')
                    }
                    for channel_id in channels_dict]

    return { 'channels': channels }

def channels_create_v1(auth_user_id, name, is_public):
    '''
    Creates a new channel, generating a channel_id and storing the information in
    the datastore. Returns the channel_id.

    Arguments:
        auth_user_id    (int)   - authorised user id
        name            (str)   - channel name
        is_public       (bool)  - public/private status

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name is not a string
        TypeError   - occurs when is_public is not a bool
        InputError  - occurs when name is not between 1 and 20 characters

    Return value:
        Returns channel_id on success
    '''

    # check for correct input types
    check_type(auth_user_id, int)
    check_type(name, str)
    check_type(is_public, bool)

    if len(name) < 1 or len(name) > 20 :
        raise InputError ('name is not between 1 and 20 characters')

    owner = data_store.get_user_from_u_id(auth_user_id)

    # ASSUMPTION: channel_id starts from 1
    new_id = len(data_store.get_channels_from_channel_id_dict()) + 1
    
    data_store.insert_channel(new_id, name, is_public, [], [owner], [owner])

    data_store.update_user_stats_channels_joined(auth_user_id)

    return { 'channel_id': new_id }
