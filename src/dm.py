from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

def dm_create_v1(auth_id, u_ids):
    '''
    Creates a DM with owner auth_id and invites
    all members in u_ids to the DM. DM name is
    created from the concatenation of handle_strs.
    Returns the dm_id.

    Arguments:
        auth_id     (int)   - authorized user id
        u_ids       (list)  - list of authorized user ids

    Exceptions:
        TypeError   - Occurs when auth_id is not an int
        TypeError   - Occurs when u_ids is not a list
        AccessError - Occurs when auth_id is invalid
        InputError  - Occurs when an u_id in u_ids is invalid

    Return Value:
        Returns dm_id on success

    '''
    check_type(auth_id, int)
    check_type(u_ids, list)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError ('Invalid auth_user_id')

    user_info = data_store.get_users_from_u_id_dict()

    if any (data_store.is_invalid_user_id(u_id) for u_id in u_ids):
        raise InputError ('an u_id in u_ids does not refer to a valid user')

    # Obtaining the handle_strs for all members in channel
    u_ids.append(auth_id)
    handle_str_list = sorted([user_info.get(u_id).get('handle_str') for u_id in u_ids])
    user_list = [data_store.get_user_from_u_id(u_id) for u_id in u_ids]

    # Creating the channel name and dm_id (ALL DM_ID ARE NEGATIVE AND START AT -1)
    dm_name = ', '.join(handle_str_list)
    dm_id = (len(data_store.get_dms_from_dm_id_dict()) + 1) * -1

    data_store.insert_dm(auth_id, dm_id, user_list, dm_name)

    return {
        'dm_id': dm_id
    }

def dm_details_v1(auth_id, dm_id):
    '''
    Returns the details of a dm given a valid dm_id

    Arguments:
        auth_id     (int)   - authorized user id
        dm_id       (int)   - refers to a dm

    Exceptions:
        TypeError   - Occurs when auth_id is not an int
        TypeError   - Occurs when dm_id is not an int
        AccessError - Occurs when auth_id is invalid
        InputError  - Occurs when dm_id does refer to a valid DM
        AccessError - Occurs when dm_id is valid but auth_id is not a member of the DM

    Return Value:
        Returns {names, members} on success

    '''
    check_type(auth_id, int)
    check_type(dm_id, int)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError ('Invalid auth_user_id')

    if data_store.is_invalid_dm(dm_id):
        raise InputError ('dm_id does not refer to valid DM')

    if data_store.is_user_member_of_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the DM')

    return data_store.get_dm_from_dm_id(dm_id).get('details')
        

def dm_list_v1(token):
    '''
    Returns a list of DMs that the user is a member of
    '''
    dm_list = { 'dms': [] }

    u_id = data_store.get_uid_from_token(token)
    if u_id == -1:
        raise AccessError("Invalid auth user id")

    dms = data_store.get_dms_from_dm_id_dict()

    for dm_id in dms:
        for member in dm_id['details']['members']:
            if member['u_id'] == u_id:
                dm_list['dms'].append(
                    {
                        'dm_id': dm_id,
                        'name': dm_id['details']['name']
                    }
                )

    return dm_list

def dm_messages_v1(token, dm_id, start):
    '''
    Returns a list of messages between index 'start' and up to 'start' + 50 from a
    given DM that the authorised user has access to. Additionally returns
    'start', and 'end' = 'start' + 50

    '''

    if start < 0:
        raise InputError('start is a negative integer')

    # need to check if dm id exists and auth_id is in dm

    messages = data_store.get_messages_from_channel_or_dm_id(dm_id)
    no_of_messages = len(messages)

    end = start + 50

    if start > no_of_messages:
        raise InputError('start is greater than the total number of messages in the channel')

    # accounts for when given empty channel and start = 0
    elif start + 50 >= no_of_messages:
        end = -1
    
    return {
        'messages' : messages,
        'start': start,
        'end' : end
        }

def dm_leave_v1(auth_id, dm_id):
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

def dm_remove_v1(auth_id, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

    Arguments:
        auth_id     (int)   - authorized user id
        dm_id       (int)   - refers to a dm

    Exceptions:
        TypeError   - Occurs when auth_id is not an int
        TypeError   - Occurs when dm_id is not an int
        AccessError - Occurs when auth_id is invalid
        InputError  - Occurs when dm_id does refer to a valid DM
        AccessError - Occurs when dm_id is valid but auth_id is not a creator of the DM

    Return Value:
        Retursn nothing on success
    '''
    check_type(auth_id, int)
    check_type(dm_id, int)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError ('Invalid auth_user_id')

    if data_store.is_invalid_dm(dm_id):
        raise InputError ('dm_id does not refer to valid DM')

    if data_store.is_user_member_of_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the DM')

    # ^^ yo inked from aleks code. if this is boken check his code.

    details_dict = data_store.get_dm_from_dm_id(dm_id).get('details')
    members = details_dict['members']
    for person in members:
        if person['u_id'] == auth_id:
            person.clear()
            return {}

    if not data_store.is_user_owner_of_channel_or_dm(auth_id, dm_id):
        raise AccessError ('dm_id is valid and the authorised user is not creator of the DM')

    data_store.remove_dm(dm_id)

    return {}
