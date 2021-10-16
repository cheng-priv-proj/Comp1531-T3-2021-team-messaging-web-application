from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

def users_all_v1(auth_id):
    '''
    Returns a list of all users and their associated details
    '''

    user_list = []
    for user in data_store.get_users_from_u_id_dict():
        user_list.append(user)
    
    return user_list