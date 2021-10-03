from src.data_store import data_store
import re

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
def clear_v1():
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
    
    duplicate_count = -1
    for user_info in data_store.get_users_from_u_id_dict().values():
        potential_duplicate_handle = base_handle_str_generation(user_info.get('name_first'), user_info.get('name_last'))
        if base_handle_str == potential_duplicate_handle:
            duplicate_count += 1

    if duplicate_count > -1:
        base_handle_str = base_handle_str + str(duplicate_count)
    
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
