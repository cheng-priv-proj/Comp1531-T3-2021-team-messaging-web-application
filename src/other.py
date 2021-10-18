from src.data_store import data_store
import re
from src.error import AccessError
def clear_v1():
    '''
    Resets the internal data of the application to its initial state, clearing the
    datastore

    Arguments:
        none

    Return value:
    Returns nothing on success
    '''
    data_store.hard_reset()
    
    return {}

# helper function to generate handles for auth_register
def handle_str_generation(firstname, lastname):
    '''
    Generates a handle string given a first name and last name

    Arguments:
        firstname (str), lastname (str)
    
    Exceptions:
        none

    Return value:
        Returns an unique handle string
    '''

    check_type(firstname, str)
    check_type(lastname, str)

    base_handle_str = base_handle_str_generation(firstname, lastname)
    handle_str = handle_prevent_duplicates(base_handle_str)
    print(handle_str)
    return handle_str

# Returns a nonduplicate handle_str
def handle_prevent_duplicates(base_handle_str):
    '''
    Given a handle string adds a number at the end to guarantee uniqueness

    Arguments:
        base_handle_str (str)

    Exceptions:
        none

    Return value:
        Returns an unique handle string
    '''
    duplicate_count = -1
    duplicate_exists = True
    handle_str = base_handle_str

    while duplicate_exists:
        duplicate_exists = False
        for user_info in data_store.get_users_from_u_id_dict().values():
            if handle_str == user_info.get('handle_str'):
                duplicate_count += 1
                duplicate_exists = True
                break
        
        handle_str = base_handle_str + str(duplicate_count)

    if duplicate_count > -1:
        base_handle_str += str(duplicate_count)
    
    return base_handle_str

# handle_str_generation helper function
def base_handle_str_generation(firstname, lastname):
    '''
    Given a first and last name returns a nonunique handle_str

    Arguments:
        firstname (str), lastname (str)

    Exceptions:
        None

    Return value:
        A nonunique handle string (str)
    '''
    base_handle = (firstname + lastname).lower()
    base_handle = re.sub(r'\W+', '', base_handle)

    if len(base_handle) > 20:
        base_handle = base_handle[0:20]

    return base_handle

# helper function to handle TypeError exceptions
def check_type(var, var_type):
    '''
    Ensures that var is of var_type

    Argument: 
        var (arbitrary type), var_type (type)

    Exceptions:
        TypeError

    Return value:
        Returns nothing on success
    '''
    if type(var) != var_type:
        raise TypeError 

# helper function to handle token to auth_id conversion
# raises an AccessError if token is invalid
def token_to_auth_id(token):
    '''
    Returns the corresponding auth_user_id of a token.

    Argument: 
        var (arbitrary type), var_type (type)

    Exceptions:
        AccessError     - occurs when token is invalid

    Return value:
        Returns auth_user_id on success
    '''

    if data_store.is_token_invalid(token):
        print(token)
        raise AccessError
    
    return data_store.get_u_id_from_token(token)


stream_owner = 1
stream_member = 2
