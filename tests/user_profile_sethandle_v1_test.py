import pytest
import requests

from src.config import url

# Extracts the token from a given dictionary.
@pytest.fixture
def extract_token():
    def extract_token_id_function(token_dict):
        return token_dict['token']
    return extract_token_id_function

# Extracts the token from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_u_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_u_id_function

# Call user profile
@pytest.fixture
def user_profile():
    def user_profile_function(token, u_id):
        return requests.get(url + 'user/profile/v1', params = {
            'token': token,
            'u_id': u_id
         })
    return user_profile_function

# Call user set handle
@pytest.fixture
def user_profile_sethandle():
    def user_profile_sethandle_function(token, handle_str):
        return requests.put(url + 'user/profile/sethandle/v1', json = {
            'token': token,
            'handle_str': handle_str
         })
    return user_profile_sethandle_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Registers an user and returns their registration info, auth_id and token and handle_str
# Assumes handle_str does not require additional processing past concatenation
@pytest.fixture
def register_user():
    def register_user_function(email, name_first, name_last):
        registration_info = {
            'email': email, 
            'password': 'password', 
            'name_first': name_first,
            'name_last': name_last }
        owner_id_dict = requests.post(url + 'auth/register/v2', json = registration_info).json()
        
        owner_id_dict['handle_str'] = registration_info.get('name_first') + registration_info.get('name_last')
        return {**owner_id_dict, **registration_info}
    return register_user_function

def test_user_profile_sethandle_basic_functionality(clear, register_user, user_profile_sethandle, user_profile, extract_user, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    user_profile_sethandle(extract_token(owner_info), 'owneronen')

    assert user_profile(extract_token(owner_info), extract_user(owner_info)).json().get('user') == {
        'u_id': extract_user(owner_info),
        'handle_str': 'owneronen',
        'name_first': 'owner',
        'name_last': 'one',
        'profile_img_url': user_profile(extract_token(owner_info), extract_user(owner_info)).json().get('user').get('profile_img_url'),
        'email': 'owner@gmail.com'
    }

def test_user_profile_sethandle_invalid_token(clear, user_profile_sethandle):
    '''
    Test case where token is not valid.

    Expects: 
        AccessError (403 error)
    '''

    assert user_profile_sethandle('asdasda', 'asdasda').status_code == 403

def test_user_profile_sethandle_handle_str_short(clear, register_user, extract_token, user_profile_sethandle):
    '''
    Test case that expects an input error when the handle string is too short.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert user_profile_sethandle(extract_token(owner_info), '').status_code == 400

def test_user_profile_sethandle_handle_str_long(clear, register_user, user_profile_sethandle, extract_token):
    '''
    Test case that expects an input error when the handle string is too long.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert user_profile_sethandle(extract_token(owner_info), 'a' * 21).status_code == 400

def test_user_profile_sethandle_duplicate(clear, register_user, user_profile_sethandle, extract_token):
    '''
    Test case that expects an input error when the handle string is a duplicate.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    register_user('user1@gmail.com', 'user', 'one')

    assert user_profile_sethandle(extract_token(owner_info), 'userone').status_code == 400

def test_user_profile_sethandle_nonalphanumeric(clear, register_user, user_profile_sethandle, extract_token):
    '''
    Test case that expects an input error when the handle string is non alphanumerical.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    
    assert user_profile_sethandle(extract_token(owner_info), '*1#$;').status_code == 400

def test_user_profile_sethandle_invalid_handle_str_and_token(clear, user_profile_sethandle):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    assert user_profile_sethandle('asdasd', '').status_code == 403

