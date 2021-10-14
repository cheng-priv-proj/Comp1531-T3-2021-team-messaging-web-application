import pytest
import requests
import operator

from src.config import url


# Extracts the token from a given dictionary.
@pytest.fixture
def extract_token():
    def extract_token_id_function(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_token_id_function

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_auth_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_auth_user_id_function

# Call users profile
@pytest.fixture
def user_profile():
    def user_profile_function(token, u_id):
        return requests.get(url + 'users/all/v1', params = {
            'token': token,
            'u_id': u_id
         })
    return user_profile_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Registers an user and returns their registration info, auth_id and token and handle_str
# Assumes handle_str does not require additional processing past concatenation
@pytest.fixture
def register_user():
    def register_user_function(email, name_first, name_last):
        registration_info = {
            'username': email, 
            'password': 'password', 
            'name_first': name_first,
            'name_last': name_last }
        owner_id_dict = requests.post(url + 'auth/register/v2', json = registration_info).json()
        if owner_id_dict.status_code == 400 or owner_id_dict.status_code == 403:
            return {}
        
        owner_id_dict['handle_str'] = registration_info.get('name_first') + registration_info.get('name_last')
        return {**owner_id_dict, **registration_info}
    return register_user_function

# Removes token and password key value pairs
@pytest.fixture
def user_info_to_user_datatype():
    def user_info_to_user_datatype_function(user_info):
        user_info.pop('token')
        user_info.pop('password')
        
        return user_info
    return user_info_to_user_datatype_function


def test_user_info_basic_check(clear, register_user, user_info_to_user_datatype, user_profile, extract_user, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_profile = user_profile(extract_token(owner_info), extract_user(owner_info)).json()

    assert owner_profile == user_info_to_user_datatype(owner_info)

def test_user_info_invalid_token(clear, register_user, user_profile, extract_user):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    
    assert user_profile('123123', extract_user(owner_info)).status_code == 403

def test_user_info_invalid_u_id(clear, register_user, user_profile, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    
    assert user_profile(extract_token(owner_info), 123123123).status_code == 400

def test_user_info_invalid_token_and_invalid_u_id(clear, register_user, user_profile):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert user_profile('123123', 1231231) == 403

def test_user_different_token_from_u_id(clear, register_user, user_info_to_user_datatype, user_profile, extract_user, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    userone_info = register_user('user@gmail.com', 'user', 'two')

    owner_profile = user_profile(extract_token(userone_info), extract_user(owner_info)).json()
    assert owner_profile == user_info_to_user_datatype(owner_profile)

    userone_profile = user_profile(extract_token(owner_info), extract_user(userone_info)).json()
    assert userone_profile == user_info_to_user_datatype(userone_info)

