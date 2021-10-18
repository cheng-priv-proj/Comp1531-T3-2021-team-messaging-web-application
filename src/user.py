from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type
import re

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
    
    if data_store.is_invalid_user_id(u_id):
        raise InputError('u_id is invalid')

    return data_store.get_user_from_u_id(u_id)


def users_all_v1(auth_id):
    '''
    Returns a list of all users and their associated details
    '''
    check_type(auth_id, int)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError('auth_user_id is invalid')

    user_list = []
    for user in data_store.get_users_from_u_id_dict():
        user_list.append(user)
    
    return user_list

def user_profile_setemail_v1(auth_id, email):
    '''
    Updates authorised user's email
    '''
    check_type(auth_id, int)
    check_type(email, str)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError('auth_user_id is invalid')

    if not re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError ('incorrect email format')

    if data_store.is_duplicate_email(email):
        raise InputError ('email is already being used by another user')

    data_store.update_value(auth_id, 'email', email)

    password = ''
    email_dict = data_store.get_logins_from_email_dict()
    for login in email_dict:
        if login['auth_user_id'] == auth_id:
            password = login['password']

    data_store.insert_login(email, auth_id, password)
    
def user_profile_sethandle_v1(auth_id, handle_str):
    '''
    Updates authorised user's handle
    '''
    check_type(auth_id, int)
    check_type(handle_str, str)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError('auth_user_id is invalid')

    if len(handle_str) < 3:
        raise InputError('Handle str shorter than 3 characters')
    if len(handle_str) > 20:
        raise InputError('Handle str longer than 20 characters')
    if handle_str.isalnum() == False:
        raise InputError('Handle str not alphanumeric')
    for user in data_store.get_users_from_u_id_dict().values():
        if user['Handle_str'] == handle_str:
            raise InputError('Handle str already being used')

    data_store.update_value(auth_id, 'Handle_str', handle_str)
