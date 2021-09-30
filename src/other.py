from src.data_store import data_store
import re

def clear_v1():
    store = data_store.get()
    for element in store:
        store[element] = {}
    data_store.set(store)


def base_handle_str_generation(firstname, lastname):
    base_handle = (firstname + lastname).lower()
    base_handle = re.sub(r'\W+', '', base_handle)

    if len(base_handle) > 20:
        base_handle = base_handle[0:20]

    return base_handle

def handle_str_generation(firstname, lastname):
    if type(firstname) != str or type(lastname) != str:
        raise TypeError

    base_handle_str = base_handle_str_generation(firstname, lastname)
    
    duplicate_count = -1
    for user_info in data_store.get_users_from_u_id_dict().values():
        potential_duplicate_handle = base_handle_str_generation(user_info.get('name_first'), user_info.get('name_last'))
        if base_handle_str == potential_duplicate_handle:
            duplicate_count += 1

    if duplicate_count > -1:
        base_handle_str = base_handle_str + str(duplicate_count)
    
    return base_handle_str


