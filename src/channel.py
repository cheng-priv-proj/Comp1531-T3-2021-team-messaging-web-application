from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from copy import deepcopy

def channel_invite_v1(inviter_auth_user_id, channel_id, invitee_u_id):
    # Checking valid input types: (ASSUMPTION: Returns nothing)
    if type(inviter_auth_user_id) != int:
        raise TypeError('Auth_user_id must be an integer')
    if type(channel_id) != int:
        raise TypeError('Channel_id must be an integer')
    if type(invitee_u_id) != int:
        raise TypeError('U_id must be an integer')
    if not data_store.isValid_auth_user_id(inviter_auth_user_id):
        raise AccessError('Invalid auth_user_id')


    invitee_user_info = data_store.get_users_from_u_id_dict().get(invitee_u_id)
    inviter_u_id = data_store.get_u_id_from_auth_dict().get(inviter_auth_user_id).get('u_id')
    channels = data_store.get_channels_from_channel_id_dict()
    
    # Checking if channel_id is valid
    if channel_id not in channels:
        raise InputError
    
    channel_details = channels.get(channel_id)
    
    # Checking if invitee_u_id is valid 
    if invitee_user_info is None:
        raise InputError
    # Checking if invitee is already a member of channel
    if data_store.check_user_is_member_of_channel(channel_id, invitee_u_id):
        raise InputError
    # Checking if channel_id is valid
    if channel_details is None:
        raise InputError
    # Checks whether invitor is a member of channel
    if not data_store.check_user_is_member_of_channel(channel_id, inviter_u_id):
        raise AccessError
    
    channel_details['all_members'].append(invitee_user_info)

def channel_details_v1(auth_user_id, channel_id):

    # check for correct input types
    if type(auth_user_id) != int or type(channel_id) != int:
        raise TypeError

    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError
        
    channels = data_store.get_channels_from_channel_id_dict()
    if channel_id not in channels:
        raise InputError

    u_ids = data_store.get_u_id_from_auth_dict()
    u_id = u_ids.get(auth_user_id)['u_id']
    
    if not data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise AccessError

    channel = channels.get(channel_id)

    # the 'messages' key value pair is not part of the function output
    channel_details = deepcopy(channel)
    channel_details.pop('messages')

    return channel_details

def channel_messages_v1(auth_user_id, channel_id, start):
    # type test(not sure if required)
    if type(auth_user_id) != int or type(channel_id) != int or type(start) != int:
        raise TypeError('incorrect input type')
    if not data_store.isValid_auth_user_id(auth_user_id):
        raise AccessError

    if start < 0:
        raise InputError('start is a negative integer')


    # Checking if the channel id exists
    channels_dict = data_store.get_channels_from_channel_id_dict()

    exist_count = [*channels_dict].count(channel_id)
    if exist_count == 0:
        raise InputError('channel_id does not refer to a valid channel')
    else:
        found_channel = channels_dict[channel_id]

    # Checking that auth_id exists in channel
    u_id_from_auth = data_store.get_user_info_from_auth_id(auth_user_id).get('u_id')
    if (data_store.check_user_is_member_of_channel(channel_id, u_id_from_auth)) == False:
        raise AccessError('the authorised user is not a member of the channel')

    no_of_messages = len(found_channel['messages'])
    if no_of_messages < start:
        raise InputError('start is greater than the total number of messages in the channel')
    elif no_of_messages > (start + 50):
        no_of_messages = start + 50
    # this the >= operator is to account for the case where index 0 is given to an empty channel list
    elif no_of_messages <= start + 50 and no_of_messages >= start:
        no_of_messages = -1
    
    message_dict = {'messages' : found_channel['messages'], 'start': start, 'end' : no_of_messages}

    return message_dict

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
