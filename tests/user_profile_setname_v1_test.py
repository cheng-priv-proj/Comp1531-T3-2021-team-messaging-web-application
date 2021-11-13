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
def user_profile_setname():
    '''
    Call user profile setname
    '''
    def user_profile_setname_function(token, name_first, name_last):
        return requests.put(url + 'user/profile/setname/v1', json = {
            'token': token,
            'name_first': name_first,
            'name_last': name_last
         })
    return user_profile_setname_function

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
        owner_id_dict = requests.post(url + 'auth/register/v2', json = registration_info).json()
        
        owner_id_dict['handle_str'] = registration_info.get('name_first') + registration_info.get('name_last')
        return {**owner_id_dict, **registration_info}
    return register_user_function

def test_user_profile_setname_basic_functionality(clear, register_user, user_profile, user_profile_setname, extract_user, extract_token):
    '''
    Standard valid test case.

    Expects: 
        Correct output from user/profile.
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    user_profile_setname(extract_token(owner_info), 'ownera', 'asdd')

    assert user_profile(extract_token(owner_info), extract_user(owner_info)).json().get('user') == {
        'u_id': extract_user(owner_info),
        'handle_str': 'ownerone',
        'name_first': 'ownera',
        'name_last': 'asdd',
        'profile_img_url': user_profile(extract_token(owner_info), extract_user(owner_info)).json().get('user').get('profile_img_url'),
        'email': 'owner@gmail.com',
    }

def test_user_profile_setname_invalid_token(clear, user_profile_setname):
    '''
    Test case where token is not valid.

    Expects: 
        AccessError (403 error)
    '''

    assert user_profile_setname('asdasd', 'owner', 'one').status_code == 403

def test_user_profile_setname_invalid_token_and_name(clear, user_profile_setname):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    assert user_profile_setname('asdasd', '', '').status_code == 403

def test_user_profile_setname_too_long(clear, user_profile_setname, register_user, extract_token):
    '''
    Test case that expects an input error when the name string is too long.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert user_profile_setname(extract_token(owner_info), 'owner', 'a' * 51).status_code == 400
    assert user_profile_setname(extract_token(owner_info), 'a' * 51, 'one').status_code == 400

def test_user_profile_setname_too_short(clear, user_profile_setname, register_user, extract_token):
    '''
    Test case that expects an input error when the name string is too short.

    Expects: 
        InputError (400 error)
    '''

    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert user_profile_setname(extract_token(owner_info), '', 'one').status_code == 400
    assert user_profile_setname(extract_token(owner_info), 'owner', '').status_code == 400



    