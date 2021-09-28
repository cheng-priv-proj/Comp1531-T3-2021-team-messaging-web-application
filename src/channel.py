from data_store import data_store
from error import InputError
from error import AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    # Checking valid input types: (ASSUMPTION: Returns nothing)
    if type(auth_user_id) != int:
        raise TypeError('Auth_user_id must be an integer')
    if type(channel_id) != int:
        raise TypeError('Channel_id must be an integer')
    if type(u_id) != int:
        raise TypeError('U_id must be an integer')

    invitee_user_info = data_store.get_u_id_dict().get(u_id)
<<<<<<< HEAD

    if invitee_user_info is None or data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise InputError

=======

    if invitee_user_info is None:
        raise InputError

>>>>>>> 29f569d (temp)
    
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
    # CHecking valid input types: (ASSUMPTION: Returns nothing)
    if type(auth_user_id) != int or type(channel_id) != int:
        return

    channel_details = data_store.get_channel_id_dict().get(channel_id)

    # Checking invalid auth_id: (ASSUMPTION: Raises InputError)
    if data_store.get_auth_user_id_dict().get(auth_user_id) == None:
        raise(InputError)

    # Checking if valid channel_id or if user already in channel_details
    if channel_details == None or data_store.check_user_is_member_of_channel(channel_id, u_id):
        raise(InputError)

    u_id = data_store.get_auth_user_id_dict().get(auth_user_id)
    user_info = data_store.get_user_info_dict().get(u_id)
    channel_details['all_members'].append(user_info)
    
    return {
    }
