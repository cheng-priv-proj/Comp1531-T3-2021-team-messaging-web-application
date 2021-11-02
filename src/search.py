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

    return { 'messages': []}