from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type
from src.message import message_send_v1

import threading
from datetime import datetime, time, timezone
from time import sleep

################# Standup Thread ###############################################

class Standup (threading.Thread):
    def __init__(self, u_id, channel_id, length):
        threading.Thread.__init__(self)
        self.u_id = u_id
        self.channel_id = channel_id
        self.length = length

    def run(self):
        print('standup thread started for channel_id ', self.channel_id)

        send_message_buffer(self.u_id, self.channel_id, self.length)

        print('standup thread exiting for channel_id ', self.channel_id)
    
def send_message_buffer(u_id, channel_id, length):
    sleep(length)
    
    standup = data_store.get_standup_from_channel_id(channel_id)

    if len(standup.get('messages')) != 0:
        message_send_v1(u_id, channel_id, standup.get('messages'))

    data_store.remove_standup(channel_id)

################################################################################

def standup_start_v1(auth_user_id, channel_id, length):
    '''
    For a given channel, start the standup period for the next 'length' seconds

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id
        length          (int)   - length of standup in seconds
    
    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id, length are not ints
        InputError  - occurs when channel_id does not refer to a valid channel
        InputError  - occurs when length is a negative integer
        InputError  - occurs when an active standup is currently running in the
                      channel
        AccessError - occurs when channel_id is valid and the authorised user is
                      not a member of the channel
    
    Returns { time_finish } on success        
    '''
    
    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(length, int)

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id does not refer to a valid channel')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid and the authorised user is not a member of the channel')

    if length < 0:
        raise InputError('length is a negative integer')

    if data_store.is_standup_active(channel_id):
        raise InputError('active standup is currently running in the channel')
    

    time_finish = int(datetime.now(timezone.utc).timestamp()) + length

    data_store.insert_standup(channel_id, time_finish)

    new_standup = Standup(auth_user_id, channel_id, length)
    new_standup.start()

    return { 'time_finish' : time_finish }

def standup_active_v1(auth_user_id, channel_id):
    '''
    For a given channel, return whether a standup is active in it, and what time
    the standup finishes. If no standup is active, then time_finish returns
    None.

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id
    
    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        InputError  - occurs when channel_id does not refer to a valid channel
        AccessError - occurs when channel_id is valid and the authorised user is
                      not a member of the channel
    
    Returns { is_active, time_finish } on success        
    '''
    check_type(auth_user_id, int)
    check_type(channel_id, int) 
    
    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id does not refer to a valid channel')
    
    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid and the authorised user is not a member of the channel')
    
    is_active = data_store.is_standup_active(channel_id)
    time_finish = None if not is_active else data_store.get_standup_from_channel_id(channel_id).get('time_finish')
    
    return {
        'is_active': is_active,
        'time_finish': time_finish
    }

def standup_send_v1(auth_user_id, channel_id, message):
    '''
    Sending a message to get buffered in the standup queue, assuming a standup
    is currently active. 

    Arguments:
        auth_user_id    (int)   - authorised user id
        channel_id      (int)   - unique channel id
        message         (str)   - message string
    
    Exceptions:
        TypeError   - occurs when auth_user_id, channel_id are not ints
        TypeError   - occurs when message is not a str
        InputError  - occurs when channel_id does not refer to a valid channel
        InputError  - occurs when length of message is over 1000 characters
        InputError  - occurs when an active standup is not currently running in
                      the channel
        AccessError - occurs when channel_id is valid and the authorised user is
                      not a member of the channel
    
    Returns {} on success        
    '''

    check_type(auth_user_id, int)
    check_type(channel_id, int)
    check_type(message, str)

    if data_store.is_invalid_channel_id(channel_id):
        raise InputError('channel_id does not refer to a valid channel')

    if not data_store.is_user_member_of_channel(channel_id, auth_user_id):
        raise AccessError('channel_id is valid and the authorised user is not a member of the channel')

    if len(message) > 1000:
        raise InputError('length of message is over 1000 characters')

    if not data_store.is_standup_active(channel_id):
        raise InputError('an active standup is not currently running in the channel')
    

    standup = data_store.get_standup_from_channel_id(channel_id)
    handle = data_store.get_user_from_u_id(auth_user_id).get('handle_str')

    if standup['messages'] != '':
        standup['messages'] += '\n'

    standup['messages'] += f'{handle}: {message}'

    return {}