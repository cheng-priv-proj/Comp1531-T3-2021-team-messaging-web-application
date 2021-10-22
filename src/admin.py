from re import U
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import check_type



def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):
    '''
    admin/userpermission/change/v1
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Method: POST

    Arguments:
        token           (str) - unique user token
        u_id            (int) - unique user identifier
        permission_id   (int) - integer specifying permission type

    Exceptions:
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user who is the only global owner and they are being demoted to a user
        InputError - Occurs when permission_id is invalid
        
        AccessError - Occurs when the authorised user is not a global owner

    Return Value:
        Returns {} on successful change. 
    '''

    check_type(auth_user_id, int)
    check_type(u_id, int)
    check_type(permission_id, int)

    # order of these errors are really dodgy need to double check.
    if data_store.is_stream_owner(auth_user_id) == False:
        raise AccessError('Token(auth_id) is not a global owner')

    if data_store.is_invalid_user_id(u_id):
        raise InputError ('u_id is invalid')
    
    if permission_id != 1 and permission_id != 2:
        raise InputError('permission_id is invalid')
    
    perm_dict = data_store.get_user_perms_from_u_id_dict()
    owner_count = 0
    for u_id_key in perm_dict:
        if perm_dict[u_id_key] == 1:
            owner_count += 1

    if data_store.is_stream_owner(u_id) and permission_id == 2:
        raise InputError ('u_id refers to a user who is the only global owner and they are being demoted to a user')
    
    data_store.insert_user_perm(u_id, permission_id)
    
    return {}


def admin_user_remove_v1(auth_user_id, u_id):
    '''
    admin/user/remove/v1

    Given a user by their u_id, remove them from the Streams. 
    This means they should be removed from all channels/DMs, and will not be included in the list of users returned by users/all. 

    Method: DELETE

    Arguments:
        token           (str) - unique user token
        u_id            (int) - unique user identifier

    Return Type:
        {}

    Exceptions:
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user who is the only global owner 
        
        AccessError - Occurs when the authorised user is not a global owner

    Return Value:
        Returns {} on successful delete.

    '''
    if data_store.is_stream_owner(auth_user_id) == False:
        raise AccessError('Token(auth_id) is not a global owner')
    if data_store.is_invalid_user_id(u_id):
        raise InputError (' u_id is invalid')

    perm_dict = data_store.get_user_perms_from_u_id_dict()
    owner_count = 0
    for u_id_key in perm_dict:
        if perm_dict[u_id_key] == 1:
            owner_count += 1
    
    if owner_count == 1 and data_store.is_stream_owner(u_id) == True:
        raise InputError ('u_id refers to a user who is the only global owner and they are being demoted to a user')

    data_store.admin_user_remove(u_id)

    return {}


