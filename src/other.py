from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    data_store.set(store)
