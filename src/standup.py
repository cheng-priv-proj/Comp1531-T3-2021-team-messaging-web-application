from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

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
    
    return { 'time_finish' : 0.0 }

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
    
    return {
        'is_active': False,
        'time_finish': 0.0
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

    return {}