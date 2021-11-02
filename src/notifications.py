from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.other import check_type

def notifications_get_v1(auth_user_id):
    '''
    Return the authorised user's most recent 20 notifications, ordered
    from most recent to least recent.

    Arguments:
        auth_user_id    (int)   - authorised user id

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int

    Return value:
        Returns { notifications } on success
    '''

    check_type(auth_user_id, int)

    return { 'notifications': data_store.get_notifications_from_u_id(auth_user_id).get('notifications')[:20] }