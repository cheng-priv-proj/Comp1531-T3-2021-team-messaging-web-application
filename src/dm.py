from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type, insert_invite_channel_or_dm_notifications

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
        InputError  - Occurs when an u_id in u_ids is invalid

    Return Value:
        Returns dm_id on success

    '''
    check_type(auth_id, int)
    check_type(u_ids, list)

    user_info = data_store.get_users_from_u_id_dict()

    if any (data_store.is_invalid_user_id(u_id) for u_id in u_ids):
        raise InputError ('an u_id in u_ids does not refer to a valid user')

    
    # Obtaining the handle_strs for all members in channel
    old_u_ids = u_ids
    u_ids.append(auth_id)
    handle_str_list = sorted([user_info.get(u_id).get('handle_str') for u_id in u_ids])
    user_list = [data_store.get_user_from_u_id(u_id) for u_id in u_ids]

    # Creating the channel name and dm_id (ALL DM_ID ARE NEGATIVE AND START AT -1)
    dm_id = (len(data_store.get_dms_from_dm_id_dict()) + 1) * -1
    dm_name = ', '.join(handle_str_list)

    data_store.insert_dm(auth_id, dm_id, user_list, dm_name)

<<<<<<< HEAD
    data_store.update_user_stats_dms_joined(auth_id)
=======
    for u_id in old_u_ids:
        insert_invite_channel_or_dm_notifications(dm_id, auth_id, u_id)
>>>>>>> c24ff9756deaa2f1ad54821f40af80dd331f8110

    return { 'dm_id': dm_id }

def dm_details_v1(auth_id, dm_id):
    '''
    Returns the details of a dm given a valid dm_id

    Arguments:
        auth_id     (int)   - authorized user id
        dm_id       (int)   - refers to a dm

    Exceptions:
        TypeError   - Occurs when auth_id is not an int
        TypeError   - Occurs when dm_id is not an int
        InputError  - Occurs when dm_id does refer to a valid DM
        AccessError - Occurs when dm_id is valid but auth_id is not a member of the DM

    Return Value:
        Returns {names, members} on success

    '''
    check_type(auth_id, int)
    check_type(dm_id, int)

    if data_store.is_invalid_dm_id(dm_id):
        raise InputError ('dm_id does not refer to valid DM')

    if not data_store.is_user_member_of_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the DM')

    return data_store.get_dm_from_dm_id(dm_id)

        

def dm_list_v1(auth_id):
    '''
        Returns the list of DMs that the user is a member of.

        Arguments:
            auth_id     (int)   - authorized user id

        Exceptions:
            AccessError         - Occurs when token is invalid

        Return Value:
            Returns nothing on success
    '''

    check_type(auth_id, int)

    dm_dict = data_store.get_dms_from_dm_id_dict().items()

    dms = [ {
                'dm_id': dm_id,
                'name': dm['details']['name']
            }
            for dm_id, dm in dm_dict
            if data_store.is_user_member_of_dm(dm_id, auth_id)
          ]

    return { 'dms': dms }

def dm_messages_v1(auth_id, dm_id, start):
    '''
    Returns a list of messages between index 'start' and up to 'start' + 50 from a
    given DM that the authorised user has access to. Additionally returns
    'start', and 'end' = 'start' + 50

    Arguments:
        auth_id         (int)   - authorized user id
        dm_id           (int)   - unique dm id
        start           (int)   - message index (most recent message has index 0)

    Exceptions:
        TypeError   - occurs when auth_user_id, dm_id, start are not ints
        InputError  - dm_id does not refer to a valid DM
        InputError  - occurs when start is negative
        InputError  - occurs when start is greater than the total number of messages
                    in the channel
        AccessError - dm_id is valid and the authorised user is not a member of the DM

    Return value:
        Returns { messages, start, end } on success
        Returns { messages, start, -1 } if the function has returned the least
        recent message


    '''
    check_type(auth_id, int)
    check_type(dm_id, int)
    check_type(start, int)


    # check if auth and dm ids are valid and user is in dm
    if data_store.is_invalid_dm_id(dm_id):
        raise InputError ('dm_id does not refer to valid DM')

    if not data_store.is_user_member_of_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the DM')

    if start < 0:
        raise InputError('start is a negative integer')

    messages = data_store.get_messages_from_channel_or_dm_id(dm_id)
    num_messages = len(messages)

    if start > num_messages:
        raise InputError('start is greater than the total number of messages in the channel')

    # accounts for when given empty channel and start = 0
    end = start + 50 if start + 50 < num_messages else -1
    
    return {
        'messages' : messages[start: start + 50],
        'start': start,
        'end' : end
        }

def dm_leave_v1(auth_id, dm_id):
    '''
    dm/leave/v1
    Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist if this happens. 
    This does not update the name of the DM.

    Arguments:
        auth_id     (int)   - authorized user id
        dm_id       (int)   - unique dm id

    Exceptions:
        TypeError   - occurs when auth_user_id, dm_id are not ints
        InputError  - dm_id does not refer to a valid DM
        AccessError - dm_id is valid and the authorised user is not a member of the DM

    Return values:
        Returns {} on success

    '''
    check_type(auth_id, int)
    check_type(dm_id, int)

    if data_store.is_invalid_dm_id(dm_id):
        raise InputError ('dm_id does not refer to valid DM')

    if not data_store.is_user_member_of_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the DM')

    dm = data_store.get_dm_from_dm_id(dm_id)
    
    dm['members'] = [user for user in dm.get('members') if user.get('u_id') != auth_id]

    return {}

def dm_remove_v1(auth_id, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

    Arguments:
        auth_id     (int)   - authorized user id
        dm_id       (int)   - refers to a dm

    Exceptions:
        TypeError   - Occurs when auth_id is not an int
        TypeError   - Occurs when dm_id is not an int
        InputError  - Occurs when dm_id does refer to a valid DM
        AccessError - Occurs when dm_id is valid but auth_id is not a creator of the DM

    Return Value:
        Returs {} on success
    '''
    check_type(auth_id, int)
    check_type(dm_id, int)

    if data_store.is_invalid_dm_id(dm_id):
        raise InputError ('dm_id does not refer to valid DM')
    
    if not data_store.is_user_owner_of_channel_or_dm(dm_id, auth_id):
        raise AccessError ('dm_id is valid and the authorised user is not creator of the DM')

    data_store.remove_dm(dm_id)

    return {}
