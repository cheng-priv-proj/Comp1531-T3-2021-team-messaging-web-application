from data_store import data_store
from error import InputError
from error import AccessError

def channel_invite_v1(inviter_auth_user_id, channel_id, invitee_u_id):
    # Checking valid input types: (ASSUMPTION: Returns nothing)
    if type(inviter_auth_user_id) != int:
        raise TypeError('Auth_user_id must be an integer')
    if type(channel_id) != int:
        raise TypeError('Channel_id must be an integer')
    if type(invitee_u_id) != int:
        raise TypeError('U_id must be an integer')

    invitee_user_info = data_store.get_u_id_dict().get(invitee_u_id)
    inviter_u_id = data_store.get_auth_user_id_dict().get(inviter_auth_user_id)
    channel_details = data_store.get_channel_id_dict().get(channel_id)

    # Checking if invitee_u_id is valid or invitee is already a member of channel
    if invitee_user_info is None or data_store.check_user_is_member_of_channel(channel_id, invitee_u_id):
        raise InputError
    # Checking if channel_id is valid
    if channel_details is None:
        raise InputError
    # Checking if inviter_auth_id is valid
    if inviter_u_id is None:
        raise InputError
    # Checks whether invitor is a member of channel
    if data_store.check_user_is_member_of_channel(channel_id, inviter_u_id):
        raise AccessError
    
    channel_details['all_members'].append(invitee_user_info)
    
    return {
    }


def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

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
    return {
    }
