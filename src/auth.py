from src.data_store import data_store
from src.error import InputError
from src.other import handle_str_generation
import re

'''
Returns a users auth_id
Arguments:
    email (string) - users email
    password (string) - users password
Exceptions:
    Type error - occurs when email or password given are not strings
    Input error - occurs when email does not belong to a user
    Input error - occurs when password is not correct
Return value:
    Returns auth_id
'''
def auth_login_v1(email, password):
    # checking for types
    if type(email) != str:
        raise TypeError

    if type(password) != str:
        raise TypeError    

    email_dict = data_store.get_login_from_email_dict()
    
    # input error if email doesn't belong to a user
    if email not in email_dict:
        raise InputError
    
    # input error if password is wrong
    if password != email_dict.get(email).get("password"):
        raise InputError

    auth_id = email_dict.get(email).get("auth_id")

    return {
        'auth_user_id': auth_id,
    }


'''
Updates data store for a new user
Generates a u_id, auth_id and handle_str
Aguments:
    email (string) - users email
    password (string) - users password
    name_first (string) - users first name
    name_last (string) - users last name
Exceptions:
    Type error - occurs when email, password, name_first or name_last are not strings
    Input error - occurs when email entered is not a valid email
    Input error - occurs when email is already being used by another user
    Input error - occurs when password is less than 6 characters
    Input error - occurs when name_first is less than 1 character or more than 50
    Input error - occurs when name_last is less than 1 character or more than 50
Return value:
    Returns auth_id
'''
def auth_register_v1(email, password, name_first, name_last):
    # checking for types
    if type(email) != str:
        raise TypeError
    if type(password) != str:
        raise TypeError
    if type(name_first) != str:
        raise TypeError
    if type(name_last) != str:
        raise TypeError

    # input errors
    if re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        pass
    else:
        raise InputError

    
    if len(password) < 6:
        raise InputError
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError
    
    #check if email is already being used
    email_dict = data_store.get_login_from_email_dict()
    if email in email_dict:
        raise InputError

    # generate u_id, auth_id and handle_str
    u_id_dict = data_store.get_users_from_u_id_dict()
    num_keys = len(u_id_dict)
    auth_id = num_keys
    u_id = -1 * auth_id

    handle_str = handle_str_generation(name_first, name_last)

    # insert new data into dicts
    data_store.insert_user_info(u_id, email, name_first, name_last, handle_str)
    data_store.insert_u_id(u_id, auth_id)
    data_store.insert_login(email, password, auth_id)


    return {
        'auth_user_id': auth_id
    }
