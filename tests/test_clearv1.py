import pytest
import ???

from src.error import InputError
from src.error import AccessError
from data_store import data_store
from data_store import Datastore

# assumes that the data store is initially empty
def test_clearv1_functionality():
    empty_data_store = data_store.Datastore()
    auth_user_id = auth_register_v1('test@gmail.com', 123, 'first', 'last')
    channel_id = channel_create_v1(auth_user_id, 'name', True)
    clear_v1()
    
    assert empty_data_store == data_store

def test_clearv1_returns_nothing():
    assert clear_v1() == None
