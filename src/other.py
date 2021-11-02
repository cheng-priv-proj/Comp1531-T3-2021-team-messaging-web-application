from src.data_store import data_store
import re
from src.error import AccessError, InputError
from src.config import SECRET
import jwt
import hashlib

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

    if base_handle == '':
        base_handle = 'defaultname'

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
        raise AccessError ('Token is invalid')
    # data_store.get_u_id_from_token(token)
    token_dict = jwt.decode(token, SECRET, algorithms=['HS256'])

    return token_dict['auth_user_id']

def hash_str(string):
    return hashlib.sha256(string.encode()).hexdigest()

def check_email_valid(email):
    if not re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError ('incorrect email format')

def check_and_insert_tag_notifications_in_message(message, channel_or_dm_id, auth_user_id):
    '''
    Checks a message for valid tags and inserts notification if exists

    Arguments:
        message (str), channel_or_dm_id (int), auth_user_id (int)

    Exceptions:
        None

    Return value:
        None
    '''
    print('entered')
    tags = [re.sub(r'\W+', '', tag) for tag in re.findall(r'@{1}[a-z0-9]+[^0-9a-zA-Z| ]?', message)]
    tags = [tags for tag in tags if data_store.is_duplicate_handle(tag) and data_store.is_user_member_of_channel_or_dm(channel_or_dm_id, data_store.get_u_id_from_handle_str(tag))]
    for tag in tags:
        tagger_handle_str = data_store.get_user_from_u_id(auth_user_id).get('handle_str')
        message = f'{tagger_handle_str} tagged you in {data_store.get_name_from_channel_or_dm_id(channel_or_dm_id)}: {message[0:20]}'
        data_store.insert_notification(data_store.get_u_id_from_handle_str(tag[0]), message, channel_or_dm_id)

def insert_invite_channel_or_dm_notifications(channel_or_dm_id, auth_user_id, u_id):
    '''
    Inserts notification when you are invited to a dm or channeli

    Arguments:
        channel_or_dm_id (int), auth_user_id (int), u_id (int)

    Exceptions:
        None

    Return Value: 
        None
    '''
    user = data_store.get_user_from_u_id(auth_user_id)
    message = f"{user.get('handle_str')} added you to {data_store.get_name_from_channel_or_dm_id(channel_or_dm_id)}"
    data_store.insert_notification(u_id, message, channel_or_dm_id)

def insert_react_message_notification(channel_or_dm_id, auth_user_id, u_id):
    '''
    Inserts notification when users react to your message

    Arguments:
        channel_or_dm_id (int), auth_user_id (int), u_id (int)

    Exceptions:
        None

    Return Value: 
        None
    '''
    user = data_store.get_user_from_u_id(auth_user_id)
    message = f"{user.get('handle_str')} reacted to your message in {data_store.get_name_from_channel_or_dm_id(channel_or_dm_id)}"
    data_store.insert_notification(u_id, message, channel_or_dm_id)

stream_owner = 1
stream_member = 2
