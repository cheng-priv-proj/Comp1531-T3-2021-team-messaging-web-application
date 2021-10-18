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
        return requests.get(url + 'user/profile/v1', json = {
            'token': token,
            'u_id': u_id
         })
    return user_profile_function

@pytest.fixture
def set_email():
    def set_email_function(token, email):
        return requests.put(url + 'user/profile/setemail/v1', json = {
            'token': token,
            'email': email
         })
    return set_email_function

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

def test_user_setemail_test_valid(clear, register_user, extract_user, extract_token, user_profile, set_email):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    set_email(extract_token(owner_info), 'valid@email.com')

    userone_profile = user_profile(extract_token(owner_info), extract_user(owner_info)).json()

    assert userone_profile == {
        'u_id': extract_user(owner_info),
        'email': 'valid@gmail.com',
        'name_first': 'owner',
        'name_last': 'one',
        'handle_str': 'ownerone'
    }

def test_user_setemail_invalid_token(clear, set_email):

    owner_profile = set_email('123123123', 'valid@email.com')

    assert owner_profile.status_code == 403

def test_user_setemail_invalid_email(clear, register_user, set_email):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')

    assert set_email(extract_token(owner_info), 'inv$alid@gmail.com').statuscode == 400


def test_user_setemail_duplicate_email(clear, register_user, extract_user, set_email):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    user_info = ('common@gmail.com', 'user', 'one')

    assert set_email(extract_token(owner_info), 'common@gmail.com').statuscode == 400

def test_user_setemail_invalid_token_and_email(clear, set_email):

    owner_profile = set_email('123123123', 'inv$alid@email.com')

    assert owner_profile.status_code == 403