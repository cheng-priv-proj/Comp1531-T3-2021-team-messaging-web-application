from src.data_store import data_store
from src.config import url 

from src.error import InputError
from src.other import check_email_valid
from PIL import Image
import urllib.request

def user_profile_v1(auth_user_id: int, u_id: int) -> dict:
    '''
    For a valid user, returns information about their user_id, email, 
    first name, last name, and handle

    Arguments:
        auth_user_id    (int)   - authorised user id
        u_id            (int)   - unique id

    Exceptions:
        TypeError   - occurs when auth_user_id, u_id are not ints
        TypeError   - occurs when u_id does not refer to a valid user
        InputError  - occurs when u_id is invalid

    Return value:
        Returns {user} on success
    '''

    if data_store.is_invalid_profile(u_id):
        raise InputError('u_id is invalid')

    return { 'user': data_store.get_user_from_u_id(u_id) }

def users_all_v1(auth_id: int) -> dict:
    '''
    Returns a list of all users and their associated details

    Arguments:
        auth_user_id    (int)   - authorised user id
    
    Exceptions:
        TypeError   - occurs when auth_user_id is not int

    Return value:
        Returns {users} on success
    '''

    user_dict = data_store.get_users_from_u_id_dict()
    users = [user for user in user_dict.values() if not user['email'] == '']
    
    return { 'users': users }

def user_setname_v1(auth_user_id: int, name_first: str, name_last: str) -> dict:
    '''
    Update the authorised user's first and last name

    Arguments:
        auth_user_id    (int)   - authorised user id
        name_first      (str)   - string
        name_last       (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        InputError  - occurs when name_first, name_last are not between 1 and 50 characters

    Return value:
        Returns {} on success
    '''

    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError ('name_first is less than 1 character or more than 50')
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError ('name_last is less than 1 character or more than 50')
    
    data_store.update_name(auth_user_id, name_first, name_last)

    return {}

def user_setemail_v1(auth_id: int, email: str) -> dict:
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id    (int)   - authorised user id
        email           (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        InputError  - occurs when email is not valid

    Return value:
        Returns {} on success
    '''

    check_email_valid(email)

    if data_store.is_duplicate_email(email):
        raise InputError ('email is already being used by another user')

    data_store.update_email(auth_id, email)

    return {}
    
def user_sethandle_v1(auth_id: int, handle_str: str) -> dict:
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id    (int)   - authorised user id
        handle          (str)   - string

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int
        TypeError   - occurs when name_first, name_last are not str
        InputError  - occurs when handle is invalid

    Return value:
        Returns {} on success
    '''

    if len(handle_str) < 3:
        raise InputError('Handle str shorter than 3 characters')

    if len(handle_str) > 20:
        raise InputError('Handle str longer than 20 characters')

    if handle_str.isalnum() == False:
        raise InputError('Handle str not alphanumeric')

    if data_store.is_duplicate_handle(handle_str):
        raise InputError('Duplicate handle string')

    data_store.update_handle(auth_id, handle_str)

    return {}

def user_profile_uploadphoto_v1(auth_user_id: int, img_url: str, x_start: int, y_start: int, x_end: int, y_end: int) -> dict:
    '''
    Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Arguments:
        auth_user_id    (int)   - authorised user id
        img_url         (str)   - url of the image
        x_start         (int)   - lower x bound
        y_start         (int)   - lower y bound
        x_end           (int)   - upper x bound
        y_end           (int)   - upper y bound

    Exceptions:
        TypeError   - occurs when auth_user_id, x_start, x_end, y_end
                      are not ints
        TypeError   - occurs when img_url is not a str
        InputError  - occurs when handle is invalid
        InputError  - occurs when img_url returns an HTTP status other than 200
        InputError  - occurs when any of x_start, y_start, x_end, y_end are not
                      within the dimensions of the image at the URL
        InputError  - occurs when x_end is less than x_start or y_end is less
                      than y_start
        InputError  - occurs when image uploaded is not a JPG

    Return value:
        Returns {} on success
    '''

    if x_end <= x_start or y_end <= y_start:
        raise InputError('Wrong dimensions')
    
    try:
        urllib.request.urlretrieve(img_url, 'src/pickle_dump/temp.jpg')
    except Exception as user_profile_uploadphoto:
        raise InputError from user_profile_uploadphoto

    imageObject = Image.open('src/pickle_dump/temp.jpg')

    if (imageObject.format != 'JPEG'):
        raise InputError('Image is not a JPG')

    width, height = imageObject.size
    if x_start < 0 or x_start > width or x_end < 0 or x_end > width:
        raise InputError
    if y_start < 0 or y_start > height or y_end < 0 or y_end > height:
        raise InputError

    urllib.request.urlretrieve(img_url, 'src/pickle_dump/' + str(auth_user_id) + '.jpg')
    imageObject = Image.open('src/pickle_dump/' + str(auth_user_id) + '.jpg')
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save('src/pickle_dump/' + str(auth_user_id) + '.jpg')

    data_store.update_profile_img_url(auth_user_id, url + str(auth_user_id) + '.jpg')

    return {}

def user_stats_v1(auth_user_id: int) -> dict:
    '''
    Fetches the required statistics about this user's use of UNSW Streams.

    Arguments:
        auth_user_id    (int)   - authorised user id

    Exceptions:
        TypeError   - occurs when auth_user_id is not an int

    Return value:
        Returns { user_stats } on success
    '''

    return {'user_stats': data_store.get_user_stats_from_u_id(auth_user_id)}

def users_stats_v1() -> dict:
    '''
    Fetches the required statistics about the use of UNSW Streams.

    Arguments:
        auth_user_id    (int)   - authorised user id
    Exceptions:
        TypeError   - occurs when auth_user_id is not an int

    Return value:
        Returns { workspace_stats } on success
    '''

    return {'workspace_stats': data_store.get_workspace_stats()}

