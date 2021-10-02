from src.data_store import data_store
from src.error import InputError
from src.other import check_type
from src.other import handle_str_generation
from src.other import stream_owner
from src.other import stream_member
import re

'''
Given the email and password of a registered user, returns the corresponding
auth_id.
Arguments:
    email       (string)   - users email
    password    (string)   - users password

Exceptions:
    TypeError  - occurs when email or password given are not strings
    InputError - occurs when email does not belong to a user
    InputError - occurs when password is not correct

Return value:
    Returns auth_id on success
'''
def auth_login_v1(email, password):

    # check for valid input types
    check_type(email, str)
    check_type(password, str)

    email_dict = data_store.get_login_from_email_dict()
    
    # input error if email doesn't belong to a user
    if email not in email_dict:
        raise InputError ('email does not belong to a user')
    
    # input error if password is wrong
    if password != email_dict.get(email).get('password'):
        raise InputError ('password is not correct')

    auth_id = email_dict.get(email).get("auth_id")

    return { 'auth_user_id': auth_id }

'''
Updates data store with a new user's information
Generates a u_id, auth_id and handle_str.

Arguments:
    email       (string)    - users email
    password    (string)    - users password
    name_first  (string)    - users first name
    name_last   (string)    - users last name

Exceptions:
    TypeError   - occurs when email, password, name_first or name_last
                  are not strings
    InputError  - occurs when email is not a valid email
    InputError  - occurs when email is already being used by another user
    InputError  - occurs when password is less than 6 characters
    InputError  - occurs when name_first is less than 1 character
                  or more than 50
    InputError  - occurs when name_last is less than 1 character
                  or more than 50

Return value:
    Returns auth_id on success
'''
def auth_register_v1(email, password, name_first, name_last):

    # checking for valid input types
    check_type(email, str)
    check_type(password, str)
    check_type(name_first, str)
    check_type(name_last, str)

    # check for valid email format
    if not re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError ('incorrect email format')

    # check for valid password, name_first and name_last lengths
    if len(password) < 6:
        raise InputError ('password is less than 6 characters')
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError ('name_first is less than 1 character or more than 50')
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError ('name_last is less than 1 character or more than 50')
    
    # check if email is already being used
    email_dict = data_store.get_login_from_email_dict()
    if email in email_dict:
        raise InputError ('email is already being used by another user')

    # generate a unique u_id and auth_id
    auth_id = len(data_store.get_users_from_u_id_dict())
    u_id = -1 * auth_id

    handle_str = handle_str_generation(name_first, name_last)

    # insert new data into dicts
    perm = stream_owner if len(email_dict) == 0 else stream_member
    data_store.insert_user_perm(u_id, perm)
    data_store.insert_user_info(u_id, email, name_first, name_last, handle_str)
    data_store.insert_u_id(u_id, auth_id)
    data_store.insert_login(email, password, auth_id)

    return { 'auth_user_id': auth_id }
