from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import check_type, check_and_insert_tag_notifications_in_message

from datetime import datetime

import threading
from datetime import datetime, time
from time import sleep

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
        Returns { message_id } on success
    '''

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
    data_store.increment_message_count()

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.utcnow().timestamp(),
        'reacts': [],
        'is_pinned': False
    }

    data_store.insert_message(channel_id, message_dict)

    check_and_insert_tag_notifications_in_message(message, channel_id, auth_user_id)

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
        Returns { message_id } on success
    '''

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
    message_id = data_store.get_messages_count()
    data_store.increment_message_count()

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': datetime.utcnow().timestamp(),
        'reacts': [],
        'is_pinned': False
    }

    data_store.insert_message(dm_id, message_dict)

    check_and_insert_tag_notifications_in_message(message, dm_id, auth_user_id)

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
        Returns {} on success
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
        (data_store.is_stream_owner(auth_user_id) and channel_or_dm_id > 0)):
        raise AccessError ('user does not have proper permissions')

    data_store.remove_message(message_id)

    return {}

def message_edit_v1(auth_user_id, message_id, message):
    '''
    Given a message, update its text with new text. 
    If the new message is an empty string, the message is deleted.

    Arguments:
        auth_user_id    (int)   - authorised user id
        dm_id           (int)   - unique dm id
        message         (str)   - message string
    
    Exceptions:
        TypeError   - occurs when auth_user_id, dm_id are not ints
        TypeError   - occurs when message is not a str
        AccessError - occurs when dm_id is valid but the authorised user is not
                    a member of the channel
        InputError  - occurs when message is more than 1000 characters

    Return value:
        Returns {} on success
    '''

    check_type(auth_user_id, int)
    check_type(message_id, int)
    check_type(message, str)

    if data_store.is_invalid_message_id(message_id):
        raise InputError

    id = data_store.get_channel_or_dm_id_from_message_id(message_id)

    if not (data_store.is_user_sender_of_message(auth_user_id, message_id) or
        (data_store.is_user_owner_of_channel_or_dm(id, auth_user_id) or data_store.is_stream_owner(auth_user_id))): 
        raise AccessError

    messages = data_store.get_messages_from_channel_or_dm_id(id)

    if len(message) > 1000:
        raise InputError

    if message == '':
        data_store.remove_message(message_id)
    
    for original_message in messages:
        if original_message.get('message_id') == message_id:
            original_message['message'] = message
    print(11111111213091203912803)
    check_and_insert_tag_notifications_in_message(message, id, auth_user_id)

    return {}

def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    '''
    Given a message_id, shares that message to the given channel or dm with
    an optional additional message
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        og_message_id   (int)   - original message id
        message         (str)   - additional message string
        channel_id      (int)   - unique channel id
        dm_id           (int)   - unique dm id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, og_message_id, channel_id, dm_id
                      are not ints
        TypeError   - occurs when message is not a str
        InputError  - occurs when both channel_id and dm_id are invalid
        InputError  - occurs when neither channel_id nor dm_id are -1
        InputError  - occurs when og_message_id does not refer to a valid
                      message within a channel/DM that the authorised user has
                      joined
        InputError  - occurs when message is more than 1000 characters
        AccessError - occurs when the pair of channel_id and dm_id are valid and
                      the authorised user has not joined the channel or DM

    Return value:
        Returns { shared_message_id } on success
    '''

    check_type(auth_user_id, int)
    check_type(og_message_id, int)
    check_type(message, str)
    check_type(channel_id, int)
    check_type(dm_id, int)

    if channel_id != -1 and dm_id != -1:
        raise InputError('neither channel_id nor dm_id are -1')
    
    if data_store.is_invalid_channel_id(channel_id) and data_store.is_invalid_dm_id(dm_id):
        raise InputError('both channel_id and dm_id are invalid')

    id = dm_id if channel_id == -1 else channel_id

    if not data_store.is_user_member_of_channel_or_dm(id, auth_user_id):
        raise AccessError('the pair of channel_id and dm_id are valid and the authorised user has not joined the channel or DM')

    if len(message) > 1000:
        raise InputError('message is more than 1000 characters')

    og_channel_or_dm_id = data_store.get_channel_or_dm_id_from_message_id(og_message_id)

    if data_store.is_invalid_message_id(og_message_id) or not data_store.is_user_member_of_channel_or_dm(og_channel_or_dm_id, auth_user_id):
        raise InputError('og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined')

    og_message = data_store.get_message_from_message_id(og_message_id).get('message')
    print('hello?')
    shared_message_id = message_send_v1(auth_user_id, id, og_message + message) if dm_id == -1 else message_senddm_v1(auth_user_id, dm_id, og_message + message)
    print(shared_message_id)
    return { 'shared_message_id': shared_message_id.get('message_id')}

def message_react_v1(auth_user_id, message_id, react_id):
    '''
    Given a message_id, shares that message to the given channel or dm with
    an optional additional message
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        message_id      (int)   - unique message id
        react_id        (int)   - unique react id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, message_id, react_id are not ints
        InputError  - occurs when message_id is not a valid message within a
                      channel or DM that the authorised user has joined
        InputError  - occurs when react_id is not a valid react ID
        InputError  - occurs when the message already contains a react with ID 
                      react_id from the authorised user

    Return value:
        Returns {} on success
    '''

    return {}

def message_unreact_v1(auth_user_id, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of,
    remove a "react" to that particular message.
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        message_id      (int)   - unique message id
        react_id        (int)   - unique react id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, message_id, react_id are not ints
        InputError  - occurs when message_id is not a valid message within a
                      channel or DM that the authorised user has joined
        InputError  - occurs when react_id is not a valid react ID
        InputError  - occurs when the message does not contain a react with ID
                      react_id from the authorised user
    Return value:
        Returns {} on success
    '''

    return {}

def message_pin_v1(auth_user_id, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        message_id      (int)   - unique message id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, message_id, react_id are not ints
        InputError  - occurs when message_id is not a valid message within a
                      channel or DM that the authorised user has joined
        InputError  - occurs when the message is already pinned
        AccessError - occurs when message_id refers to a valid message in a
                      joined channel/DM and the authorised user does not have
                      owner permissions in the channel/DM
    Return value:
        Returns {} on success
    '''

    return {}

def message_unpin_v1(auth_user_id, message_id):
    '''
    Given a message within a channel or DM, remove its mark as pinned.
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        message_id      (int)   - unique message id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, message_id, react_id are not ints
        InputError  - occurs when message_id is not a valid message within a
                      channel or DM that the authorised user has joined
        InputError  - occurs when the message is not already pinned
        AccessError - occurs when message_id refers to a valid message in a
                      joined channel/DM and the authorised user does not have
                      owner permissions in the channel/DM
    Return value:
        Returns {} on success
    '''

    return {}

################# Standup Thread ###############################################

class DelayedMessage (threading.Thread):
    def __init__(self, u_id, channel_or_dm_id, timesent, message):
        threading.Thread.__init__(self)
        self.u_id = u_id
        self.channel_or_dm_id = channel_or_dm_id
        self.wait = timesent - datetime.utcnow().timestamp() 
        self.message = message
        self.message_id = {}

    def run(self):
        print('delayed message thread started for channel_id ', self.channel_or_dm_id)

        sleep(self.wait)
        if self.channel_or_dm_id < 0:
            self.message_id = message_senddm_v1(self.u_id, self.channel_or_dm_id, self.message)  
                 
        else:
            self.message_id = message_send_v1(self.u_id, self.channel_or_dm_id, self.message)
        data_store.decrease_message_count()
        
        print('delayed message thread exiting for channel_id ', self.channel_or_dm_id)


################################################################################


def message_sendlater_v1(auth_user_id, channel_id, message, time_sent):
    '''
    Send a message from the authorised user to the channel specified by
    channel_id automatically at a specified time in the future.
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id
        message         (str)   - message str
        time_sent       (float) - time as a unix timestamp
    
    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        TypeError   - occurs when message is not a str
        TypeError   - occurs when time_sent is not a float
        InputError  - channel_id does not refer to a valid channel
        InputError  - length of message is over 1000 characters
        InputError  - time_sent is a time in the past
        AccessError - channel_id is valid and the authorised user is not a
                      member of the channel they are trying to post to

    Returns { message_id } on success
    '''
    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(message, str)
    check_type(time_sent, float)

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id does not refer to a valid channel')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError ('channel_id is valid and the authorised user is not a member of the channel they are trying to post to')

    if len(message) > 1000:
        raise InputError('length of message is over 1000 characters')

    if time_sent - datetime.utcnow().timestamp() < 0:
        raise InputError('time_sent is a time in the past')

    delayed_message = DelayedMessage(auth_user_id, channel_id, time_sent, message)
    delayed_message.start()
    
    return {'message_id': data_store.get_messages_count()}

def message_sendlaterdm_v1(auth_user_id, dm_id, message, time_sent):
    '''
    Send a message from the authorised user to the DM specified by dm_id
    automatically at a specified time in the future.
    
    Arguments:
        auth_user_id    (int)   - authorised user id
        dm_id           (int)   - unique dm id
        message         (str)   - message str
        time_sent       (float) - time as a unix timestamp
    
    Exceptions:
        TypeError   - occurs when auth_user_id, dm_id are not ints
        TypeError   - occurs when message is not a str
        TypeError   - occurs when time_sent is not a float
        InputError  - occurs when dm_id does not refer to a valid DM
        InputError  - occurs when length of message is over 1000 characters
        InputError  - occurs when time_sent is a time in the past
        AccessError - occurs when dm_id is valid and the authorised user is not
                      a member of the DM they are trying to post to

    Returns { message_id } on success
    '''
    check_type(auth_user_id, int)
    check_type(dm_id, int)
    check_type(message, str)
    check_type(time_sent, float)

    if data_store.is_invalid_channel_id(dm_id):
        raise InputError('dm_id does not refer to a valid dm')

    if not data_store.is_user_member_of_dm(dm_id, auth_user_id):
        raise AccessError ('dm_id is valid and the authorised user is not a member of the dm they are trying to post to')

    if len(message) > 1000:
        raise InputError('length of message is over 1000 characters')

    if time_sent - datetime.utcnow().timestamp() < 0:
        raise InputError('time_sent is a time in the past')

    delayed_message = DelayedMessage(auth_user_id, dm_id, time_sent, message)
    delayed_message.start()

    return delayed_message.message_id