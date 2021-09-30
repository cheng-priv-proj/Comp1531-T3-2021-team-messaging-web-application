import pytest

from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
import src.data_store as data_store

# assumes that the data store is initially empty
def test_clearv1_functionality():
    clear_v1()
    empty_data_store = data_store.Datastore()
    auth_user_id = auth_register_v1('test@gmail.com', 1234567, 'first', 'last')
    auth_user_id2 = auth_register_v1('test2@gmail.com', 1234567, 'first', 'last')
    channel_id = channels_create_v1(auth_user_id, 'name', True)
    channel_id2 = channels_create_v1(auth_user_id2, 'name', True)
    clear_v1()
    
    assert empty_data_store == data_store

def test_clearv1_returns_nothing():
    assert clear_v1() == None
