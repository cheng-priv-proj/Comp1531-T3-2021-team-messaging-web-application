import pytest
import requests

from src.config import url 

@pytest.fixture
def extract_token():
    '''
    Extracts the token from a given dictionary.
    '''
    def extract_token_id_function(token_dict):
        return token_dict['token']
    return extract_token_id_function

@pytest.fixture
def extract_user():
    '''
    Extracts the token from a given dictionary.
    '''
    def extract_u_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_u_id_function

@pytest.fixture
def extract_profile_img_url():
    '''
    Extracts profile_img_url from a given dictionary.
    '''
    def extract_profile_img_url_function(user_profile_dict):
        return user_profile_dict['profile_img_url']
    return extract_profile_img_url_function

@pytest.fixture
def user_profile():
    '''
    Call user profile
    '''
    def user_profile_function(token, u_id):
        return requests.get(url + 'user/profile/v1', params = {
            'token': token,
            'u_id': u_id
         })
    return user_profile_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register_user():
    '''
    Registers an user and returns their registration info, auth_id and token and handle_str
    Assumes handle_str does not require additional processing past concatenation
    '''
    def register_user_function(email, name_first, name_last):
        registration_info = {
            'email': email, 
            'password': 'password', 
            'name_first': name_first,
            'name_last': name_last }
        register = requests.post(url + 'auth/register/v2', json = registration_info)
        register_dict = register.json()
        if register.status_code != 403 and register.status_code != 400:
            owner_id_profile = requests.get(url + 'user/profile/v1', params = {'token': register_dict['token'], 'u_id': register_dict['auth_user_id']})
            register_dict['profile_img_url'] = owner_id_profile.json()['user']['profile_img_url']

        register_dict['handle_str'] = registration_info.get('name_first') + registration_info.get('name_last')    
        return {**register_dict, **registration_info}
    return register_user_function

# Removes token and password key value pairs
@pytest.fixture
def user_info_to_user_datatype():
    def user_info_to_user_datatype_function(user_info):
        user_info.pop('token')
        user_info.pop('password')
        
        return user_info
    return user_info_to_user_datatype_function


def test_user_profile_test_valid(clear, register_user, user_info_to_user_datatype, extract_user, extract_token, user_profile, extract_profile_img_url):
    '''
    Standard valid test case.

    Expects: 
        Correct output from user/profile.
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    userone_info = register_user('user1@gmail.com', 'user', 'one')
    userone_profile = user_profile(extract_token(owner_info), extract_user(userone_info)).json().get('user')

    assert userone_profile == {
        'u_id': extract_user(userone_info),
        'email': 'user1@gmail.com',
        'name_first': 'user',
        'name_last': 'one',
        'profile_img_url': extract_profile_img_url(userone_info),
        'handle_str': 'userone'
    }

def test_user_profile_invalid_token(clear, register_user, user_info_to_user_datatype, extract_user, extract_token, user_profile):
    '''
    Test case where token is not valid.

    Expects: 
        AccessError (403 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_profile = user_profile('123123123', extract_user(owner_info))

    assert owner_profile.status_code == 403

def test_user_profile_invalid_u_id(clear, register_user, user_info_to_user_datatype, extract_user, extract_token, user_profile):
    '''
    Test case that expects an input error when the u_id does not exist.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    invalid_profile = user_profile(extract_token(owner_info), 123123123)

    assert invalid_profile.status_code == 400

def test_user_profile_invalid_id_and_token(clear, register_user, user_info_to_user_datatype, extract_user, extract_token, user_profile):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    invalid_profile = user_profile('123123', 212312)
    
    assert invalid_profile.status_code == 403

def test_user_profile_get_your_own_profile(clear, register_user, user_info_to_user_datatype, extract_user, extract_token, user_profile, extract_profile_img_url):
    '''
    Test case where user requests their own data.

    Expects: 
        Correct output from user/profile.
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_profile = user_profile(extract_token(owner_info), extract_user(owner_info)).json().get('user')

    assert owner_profile == {
        'u_id': extract_user(owner_info),
        'email': 'owner@gmail.com',
        'name_first': 'owner',
        'name_last': 'one',
        'profile_img_url': extract_profile_img_url(owner_info),
        'handle_str': 'ownerone'
    }

