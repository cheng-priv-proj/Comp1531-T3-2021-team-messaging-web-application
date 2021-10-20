from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import check_type

from datetime import datetime

def message_send_v1(auth_user_id, channel_id, message):
    '''
    Send a message from the authorised user to the channel specified by channel_id

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id
        message         (str)   - message string

    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        TypeError   - occurs when message is not a str
        AccessError - occurs when channel_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success'''

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(message, str)

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('invalid channel_id')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid but the authorised user is not a member of the channel')

    if len(message) < 1 or len(message) > 1000:
        raise InputError('message has invalid length')

    # message ids will start from 0
    message_id = data_store.get_messages_count()
    data_store.insert_message_count()

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.utcnow().timestamp()
    }

    data_store.insert_message(channel_id, message_dict)

    return { 'message_id': message_id}


def message_senddm_v1(auth_user_id, dm_id, message):
    '''
    Send a message from the authorised user to the dm specified by dm_id

    Arguments:
        auth_user_id    (int)   - authorised user id
        dm_id           (int)   - unique dm id
        message         (str)   - message string

    Exceptions:
        TypeError   - occurs when auth_user_id, dm_id are not ints
        TypeError   - occurs when message is not a str
        AccessError - occurs when dm_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success'''

    check_type(auth_user_id, int)
    check_type(dm_id, int)
    check_type(message, str)

    if data_store.is_invalid_dm_id(dm_id):
        raise InputError('invalid dm_id')

    if not data_store.is_user_member_of_dm(dm_id, auth_user_id):
        raise AccessError('channel_id is valid but the authorised user is not a member of the dm')

    if len(message) < 1 or len(message) > 1000:
        raise InputError('message has invalid length')

    # message ids will start from 0
    data_store.insert_message_count()
    message_id = data_store.get_messages_count()

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.utcnow().timestamp()
    }

    data_store.insert_message(dm_id, message_dict)

    return { 'message_id' : message_id }

def message_remove_v1(auth_user_id, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        auth_user_id    (int)   - authorised user id
        message_id      (int)   - unique message id

    Exceptions:
        InputError  - occurs when message_id does not refer to a valid message within a channel/DM
        InputError  - occurs when user is not a member of channel
        AccessError - occurs when user does not have proper permissions

    Return Value:
        Returns nothing on success
    '''
    check_type(auth_user_id, int)
    check_type(message_id, int)

    if data_store.is_invalid_message_id(message_id):
        raise InputError ('message_id does not refer to a valid message within a channel/DM')

    channel_or_dm_id = data_store.get_channel_or_dm_id_from_message_id(message_id)    
    if not data_store.is_user_member_of_channel_or_dm(channel_or_dm_id, auth_user_id):
        raise InputError ('user is not a member of channel')

    if not (data_store.is_user_owner_of_channel_or_dm(channel_or_dm_id, auth_user_id) or 
        data_store.is_user_sender_of_message(auth_user_id, message_id) or 
        data_store.is_stream_owner(auth_user_id)):
        raise AccessError ('user does not have proper permissions')

    data_store.remove_message(message_id)

    return {}

def message_edit_v1(auth_user_id, message_id, message):

    check_type(auth_user_id, int)
    check_type(message_id, int)
    check_type(message, str)

    if data_store.is_invalid_message_id(message_id):
        raise InputError

    id = data_store.get_channel_or_dm_id_from_message_id(message_id)

    if not (data_store.is_user_sender_of_message(auth_user_id, message_id) or
        data_store.is_user_owner_of_channel_or_dm(id, auth_user_id)
        or data_store.is_stream_owner(auth_user_id)): 
        raise AccessError

    messages = data_store.get_messages_from_channel_or_dm_id(id)

    if len(message) > 1000:
        raise InputError

    if message == '':
        data_store.remove_message(message_id)
    
    print(messages)
    for index, original_message in enumerate(messages):
        print(original_message.get('message_id'))
        if original_message.get('message_id') == message_id:
            messages[index]['message'] = message
            print(messages[index]['message'] )
            break
    

    return {}
