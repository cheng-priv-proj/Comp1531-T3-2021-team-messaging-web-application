import pytest
import requests
from src.config import url

# Assumes that the data store is initially empty.
# Testing if database is empty by comparing bit size with the bit size of an empty dict.
def test_clearv1_functionality():
    requests.delete(url + 'clear/v1')
    registration_info = {
            'username': 'email@gmail.com', 
            'password': 'password', 
            'name_first': 'name_first',
            'name_last': 'name_last' }
    owner_id_dict = requests.post(url + 'auth/register/v2', json = registration_info)
    requests.delete(url + 'clear/v1')
    assert requests.post(url + 'auth/login/v2', json = {'email': 'email@gmail.com', 'password': 'password'}).status_code == 400

 
def test_clearv1_returns_empty_dict():
    assert requests.delete(url + 'clear/v1').json() == {}
