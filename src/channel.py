from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import check_type

def channel_invite_v1(auth_user_id, channel_id, u_id):
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

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(u_id, int)

    # checking if auth_id is valid
    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('Invalid auth_user_id')
    

    # Checking if channel_id is valid
    if data_store.is_invalid_channel_id(channel_id):
        raise InputError ('channel_id is invalid')

    # Checks whether invitor is a member of channel
    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError ('channel_id is valid but the authorised user is not a member of the channel')

    # Checking if invitee_u_id is valid 
    if data_store.is_invalid_user_id(u_id):
        raise InputError ('u_id is invalid')
    
    # checking if invitee is already a member of channel
    if data_store.is_user_member_of_channel(channel_id, u_id):
        raise InputError ('u_id refers to a user who is already a member of the channel')
    
    channel = data_store.get_channel_from_channel_id(channel_id)

    channel.get('all_members').append(data_store.get_user_from_u_id(u_id))

    return {}

def channel_details_v1(auth_user_id, channel_id):
    '''
    Returns the details of a given channel that an authorised user has access to.

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id

    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        AccessError - occurs when auth_id is invalid
        InputError  - occurs when channel_id is invalid
        AccessError - occurs when channel_id is valid but the authorised user is
                    not a member of the channel

    Return value:
        Returns {name, is_public, owner_members, all_members} on success
    '''

    check_type(auth_user_id, int)
    check_type(channel_id, int)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError ('auth_id is invalid')
        
    if data_store.is_invalid_channel_id(channel_id):
        raise InputError (' channel_id is invalid')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError ('u_id is not part of the channel')

    channel = data_store.get_channel_from_channel_id(channel_id)

    return channel

def channel_messages_v1(auth_user_id, channel_id, start):
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

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(start, int)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError ('auth_id is invalid')

    # ASSUMPTION: negative start index causes an InputError exception
    if start < 0:
        raise InputError('start is a negative integer')

    # Checking if the channel id exists
    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id does not refer to a valid channel')

    # Checking that auth_id exists in channel
    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('the authorised user is not a member of the channel')

    messages = data_store.get_messages_from_channel_or_dm_id(channel_id)
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

def channel_join_v1(auth_user_id, channel_id):
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
        InputError  - occurs when user is already part of the channel

    Return value:
        Returns nothing on success
    '''

    check_type(auth_user_id, int)
    check_type(channel_id, int)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError (' auth_id is invalid')

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError ('channel_id is invalid')

    channel = data_store.get_channel_from_channel_id(channel_id)

    # Checking if user exists in all members
    if data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise InputError ('user is already part of the channel')

    # Checking if channel is public
    if not channel.get('is_public') and not data_store.is_stream_owner(auth_user_id):
        raise AccessError ('channel is not public')

    user = data_store.get_user_from_u_id(auth_user_id)
    channel.get('all_members').append(user)

    return {}

def channel_leave_v1(auth_user_id, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of,
    remove them as a member of the channel.

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id

    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        AccessError - occurs when auth_id is invalid
        InputError  - occurs when channel_id is invalid
        AccessError - occurs when channel_id is valid and the authorised user is
                      not a member of the channel

    Return value:
        Returns nothing on success
    '''

    check_type(auth_user_id, int)
    check_type(channel_id, int)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('auth_id is invalid')
    
    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id is invalid')

    if data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid and the authorised user is not a member of the channel')

    # move everything below into a data_store method?
    channel = data_store.get_channel_from_channel_id(channel_id)

    members = channel.get('all_members')

    channel['all_members'] = [member for member in members if member.get('u_id') != auth_user_id]

    if data_store.is_channel_owner(channel_id, auth_user_id):
        owners = channel.get('owner_members')

        channel['owner_members'] = [owner for owner in members if owner.get('u_id') != auth_user_id]
    
    return {}