from src.data_store import data_store
from src.error import InputError
from src.other import check_type
from src.other import handle_str_generation
from src.other import stream_owner
from src.other import stream_member
from src.other import hash_str
from src.config import SECRET
import re
import jwt

def auth_login_v1(email, password):
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

    # check for valid input types
    check_type(email, str)
    check_type(password, str)
    
    # input error if email doesn't belong to a user
    if data_store.is_invalid_email(email):
        raise InputError ('email does not belong to a user')
    
    login = data_store.get_login_from_email(email)

    # input error if password is wrong
    if hash_str(password) != login.get('password'):
        raise InputError ('password is not correct')

    auth_user_id = login.get("auth_id")

    token = jwt.encode({
                'auth_user_id': auth_user_id,
                'token_count': len(data_store.get_u_ids_from_token_dict())
                },
                 SECRET, algorithm='HS256')

    data_store.insert_token(token, auth_user_id)

    return { 'token': token,'auth_user_id': auth_user_id }

def auth_register_v1(email, password, name_first, name_last):
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
    if data_store.is_duplicate_email(email):
        raise InputError ('email is already being used by another user')

    # generate a unique auth_id
    auth_user_id = len(data_store.get_users_from_u_id_dict())
    handle_str = handle_str_generation(name_first, name_last)

    # hash the password
    encrypted_password = hash_str(password)

    # insert new data into dicts
    perm = stream_owner if auth_user_id == 0 else stream_member
    data_store.insert_user_perm(auth_user_id, perm)
    data_store.insert_user(auth_user_id, email, name_first, name_last, handle_str)
    data_store.insert_login(email, encrypted_password, auth_user_id)

    return { 'auth_user_id': auth_user_id }


def auth_logout_v1(token):
    data_store.invalidate_token(token)

    return {}