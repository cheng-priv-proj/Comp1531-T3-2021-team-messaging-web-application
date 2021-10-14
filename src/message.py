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
        AccessError - occurs when auth_user_id is invalid
        AccessError - occurs when channel_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success'''

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(message, str)
    
    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('auth_user_id is invalid')

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('invalid channel_id')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid but the authorised user is not a member of the channel')

    if len(message) < 1 or len(message) > 1000:
        raise InputError('message has invalid length')

    # message ids will start from 0
    message_id = len(data_store.get_channel_or_dm_id_from_message_id_dict())

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.now
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
        AccessError - occurs when auth_user_id is invalid
        AccessError - occurs when dm_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is less than 1 or more than 1000 characters

    Return value:
        Returns message_id on success'''

    check_type(auth_user_id, int)
    check_type(dm_id, int)
    check_type(message, str)
    
    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('auth_user_id is invalid')

    if data_store.is_invalid_dm_id(dm_id):
        raise InputError('invalid dm_id')

    if not data_store.is_user_member_of_dm(dm_id, auth_user_id):
        raise AccessError('channel_id is valid but the authorised user is not a member of the dm')

    if len(message) < 1 or len(message) > 1000:
        raise InputError('message has invalid length')

    # message ids will start from 0
    message_id = len(data_store.get_channel_or_dm_id_from_message_id_dict())

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.now
    }

    data_store.insert_message(dm_id, message_dict)

    return { 'message_id' : message_id }