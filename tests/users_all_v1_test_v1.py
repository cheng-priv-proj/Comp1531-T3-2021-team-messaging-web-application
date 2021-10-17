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

# Call users all
@pytest.fixture
def users_all():
    def users_all_function(token):
        return requests.get(url + 'users/all/v1', params = {
            'token': token
         })
    return users_all_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Registers an user and returns their registration info, auth_id and token and handle_str
# Assumes handle_str does not require additional processing past concatenation
@pytest.fixture
def register_user_return_info():
    def register_user_return_info_function(email, name_first, name_last):
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
    return register_user_return_info_function

# Removes token and password key value pairs
@pytest.fixture
def user_info_to_user_datatype():
    def user_info_to_user_datatype_function(user_info):
        user_info.pop('token')
        user_info.pop('password')
        
        return user_info
    return user_info_to_user_datatype_function

# Sort users as it is not innately ordered
@pytest.fixture
def sort_users():
    def sort_users_function(users):
        return users.sorted(key=operator.itemgetter('name_first'))
    return sort_users_function

def test_users_all_one_user(clear, register_user_return_info, users_all, extract_token, user_info_to_user_datatype, sort_users):
    owner_info = register_user_return_info('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)
    user_list = users_all(owner_token).json()['users']
    assert sort_users(user_list) == sort_users(user_info_to_user_datatype(owner_info))

def test_users_all_multiple_users(clear, register_user_return_info, users_all, extract_token, user_info_to_user_datatype, sort_users):
    owner_info = register_user_return_info('owner@gmail.com', 'owner', 'one')
    user_list = [owner_info]
    for i in range(0, 100):
        user_list.append(register_user_return_info('user' + str(i) + '@gmail.com', 'user', str(i)))

    user_token = extract_token(user_list[1])
    user_list_from_users_all = users_all(user_token).json()['users']

    assert sort_users(user_list_from_users_all) == sort_users([user_info_to_user_datatype(user) for user in user_list])

def test_users_all_works_for_non_owner(clear, register_user_return_info, users_all, extract_token, user_info_to_user_datatype, sort_users):
    owner_info = register_user_return_info('owner@gmail.com', 'owner', 'one')
    user_info1 = register_user_return_info('user1@gmail.com', 'user', 'two')
    user_info2 = register_user_return_info('user2@gmail.com', 'user', 'three')
    user_info3 = register_user_return_info('user2@gmail.com', 'user', 'four')
    user_list = [owner_info, user_info1, user_info2, user_info3]

    user_token = extract_token(user_info1)
    user_list_from_users_all = users_all(user_token).json()['users']

    assert sort_users(user_list_from_users_all) == sort_users([user_info_to_user_datatype(user) for user in user_list])

def test_users_all_works_for_failed_registration(clear, register_user_return_info, users_all, extract_token, user_info_to_user_datatype, sort_users):
    owner_info = register_user_return_info('owner@gmail.com', 'owner', 'one')
    user_info1 = register_user_return_info('user1@gmail.com', 'user', 'two')
    user_info2 = register_user_return_info('user1@gmail.com', 'user', 'three')
    user_info3 = register_user_return_info('user1@gmail.com', 'user', 'four')
    user_list = [owner_info, user_info1]

    owner_token = extract_token(owner_info)
    user_lists_from_users_all = users_all(owner_token).json()['users']

    assert sort_users(user_lists_from_users_all) == sort_users([user_info_to_user_datatype(user) for user in user_list])

def test_users_all_invalid_token(clear, register_user_return_info, users_all):
    owner_info = register_user_return_info('owner@gmail.com', 'owner', 'one')

    assert users_all(-123123).status_code() == 403
