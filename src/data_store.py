'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'login': {},
    'auth_to_user': {},
    'channel_id_to_channel_details': {},
    'uid_to_user': {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def get_email_dict(self):
        return self.initial_object['email']

    def get_auth_user_id_dict(self):
        return self.initial_object['auth_user_id']
    
    def get_channel_id_dict(self):
        return self.initial_object['channel_id']

    def get_u_id_dict(self):
        return self.initial_object['u_id']

    def update_value(dict_key, key, value):
        self.initial_object[dict_key][key] = value

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

