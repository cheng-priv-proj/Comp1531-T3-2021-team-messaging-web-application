import requests

from src.config import url

def test_check_type():
    requests.delete(url + "clear/v1")
    requests.post(url + 'auth/register/v2', json={
        'email': 1,
        'password': 'password',
        'name_first': 'owner',
        'name_last': 'one'
    }).status_code == 500
    
    requests.delete(url + "clear/v1")

    
    
    