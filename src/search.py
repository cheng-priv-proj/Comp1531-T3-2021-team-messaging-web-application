from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

def search_v1(auth_user_id, query_str):
    '''
    Given a query string, return a collection of messages in all of the
    channels/DMs that the user has joined that contain the query.

    Arguments:
        auth_user_id    (int)   - authorised user id
        query_str       (str)   - query string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when query_str is not a str
        InputError  - length of query_str is less than 1 or over 1000 characters

    Return value:
        Returns { messages } on success
    '''
    print('query_str')
    print(query_str)
    if len(query_str) > 1000 or len(query_str) < 1:
        raise InputError('length of query_str is less than 1 or over 1000 characters')


    returning_messages_list = []

    channels_dict = data_store.get_channels_from_channel_id_dict()

    channels = [{
                    'channel_id': channel_id,
                    'name': channels_dict.get(channel_id).get('name')
                }
                for channel_id in channels_dict
                if data_store.is_user_member_of_channel(channel_id, auth_user_id)
               ]

    

    for element in channels:
        messages = data_store.get_messages_from_channel_or_dm_id(element['channel_id'])
        for message in messages:
            if query_str in message['message']:
                returning_messages_list.append(message)

    dm_dict = data_store.get_dms_from_dm_id_dict().items()

    dms = [ {
                'dm_id': dm_id,
                'name': dm['details']['name']
            }
            for dm_id, dm in dm_dict
            if data_store.is_user_member_of_dm(dm_id, auth_user_id)
          ]

    for element in dms:
        messages = data_store.get_messages_from_channel_or_dm_id(element['dm_id'])
        for message in messages:
            if query_str in message['message']:
                returning_messages_list.append(message)


    return { 'messages': returning_messages_list}
