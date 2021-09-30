from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    for element in store.values():
        store[element] = {}
    data_store.set(store)
