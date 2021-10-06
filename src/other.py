from src.data_store import data_store
import re


def clear_v1():
    '''
    Resets the internal data of the application to its initial state, clearing the
    datastore

    Arguments:
        none

    Exceptions:
        none

    Return value:
        Returns nothing on success
    '''
    store = data_store.get()
    for element in store:
        store[element] = {}
    data_store.set(store)
    
    return {}

# helper function to generate handles for auth_register
def handle_str_generation(firstname, lastname):

    check_type(firstname, str)
    check_type(lastname, str)

    base_handle_str = base_handle_str_generation(firstname, lastname)
    handle_str = handle_prevent_duplicates(base_handle_str)
    print(handle_str)
    return handle_str

# Returns a nonduplicate handle_str
def handle_prevent_duplicates(base_handle_str):
    duplicate_count = -1
    duplicate_exists = True
    handle_str = base_handle_str

    while duplicate_exists:
        duplicate_exists = False
        for user_info in data_store.get_users_from_u_id_dict().values():
            if handle_str == user_info.get('han'):
                duplicate_count += 1
                duplicate_exists = True
                break
        
        handle_str = base_handle_str + str(duplicate_count)

    if duplicate_count > -1:
        base_handle_str += str(duplicate_count)
    
    return base_handle_str

# handle_str_generation helper function
def base_handle_str_generation(firstname, lastname):
    base_handle = (firstname + lastname).lower()
    base_handle = re.sub(r'\W+', '', base_handle)

    if len(base_handle) > 20:
        base_handle = base_handle[0:20]

    return base_handle

# helper function to handle TypeError exceptions
def check_type(var, var_type):
    
    if type(var) != var_type:
        raise TypeError

stream_owner = 1
stream_member = 2
