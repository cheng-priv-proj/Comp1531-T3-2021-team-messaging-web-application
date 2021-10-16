from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

def user_profile_v1(auth_user_id, u_id):
    '''
    For a valid user, returns information about their user_id, email, 
    first name, last name, and handle

    Arguments:
        auth_user_id    (int)   - authorised user id
        u_id            (int)   - unique id

    Exceptions:
        TypeError   - occurs when auth_user_id, u_id are not ints
        TypeError   - occurs when u_id does not refer to a valid user
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when u_id is invalid

    Return value:
        Returns user on success
    '''

    check_type(auth_user_id, int)
    check_type(u_id, int)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('auth_user_id is invalid')
    
    if data_store.is_invalid_user_id(auth_user_id):
        raise InputError('auth_user_id is invalid')

    return data_store.get_user_from_u_id(u_id)


def users_all_v1(auth_id):
    '''
    Returns a list of all users and their associated details
    '''

    user_list = []
    for user in data_store.get_users_from_u_id_dict():
        user_list.append(user)
    
    return user_list