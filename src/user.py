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

    print("DDDDDDDDDDDDDDDDD")

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError('auth_user_id is invalid')

    user_list = {'users': []}
    user_dict = data_store.get_users_from_u_id_dict()
    for user in user_dict:
        user_list['users'].append(
            user_dict[user]
        )
    
    print(user_list)
    return user_list

def user_setname_v1(auth_user_id, name_first, name_last):
    '''
    Update the authorised user's first and last name

    Arguments:
        auth_user_id    (int)   - authorised user id
        name_first      (str)   - string
        name_last       (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when name_first, name_last are not between 1 and 50 characters

    Return value:
        Returns nothing on success
    '''

    check_type(auth_user_id, int)
    check_type(name_first, str)
    check_type(name_last, str)

    if data_store.is_invalid_user_id(auth_user_id):
        raise AccessError('auth_user_id is invalid')
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError ('name_first is less than 1 character or more than 50')
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError ('name_last is less than 1 character or more than 50')
    
    data_store.update_name(auth_user_id, name_first, name_last)

    return {}

def user_setemail_v1(auth_id, email):
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id    (int)   - authorised user id
        email           (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when email is not valid

    Return value:
        Returns nothing on success
    '''
    check_type(auth_id, int)
    check_type(email, str)

    if data_store.is_invalid_user_id(auth_id):
        raise AccessError('auth_user_id is invalid')

    if not re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError ('incorrect email format')

    if data_store.is_duplicate_email(email):
        raise InputError ('email is already being used by another user')

    # data_store.update_value(auth_id, 'email', email)

    # password = ''
    # email_dict = data_store.get_logins_from_email_dict()
    # for login in email_dict:
    #     if login['auth_user_id'] == auth_id:
    #         password = login['password']

    # data_store.insert_login(email, auth_id, password)

    data_store.update_email(auth_id, email)

    return {}
    
def user_sethandle_v1(auth_id, handle_str):
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id    (int)   - authorised user id
        handle          (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        AccessError - occurs when auth_user_id is invalid
        InputError  - occurs when handle is invalid

    Return value:
        Returns nothing on success
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
    if data_store.is_duplicate_handle(handle_str):
        raise InputError('Duplicate handle string')

    data_store.update_handle(auth_id, handle_str)

    return {}