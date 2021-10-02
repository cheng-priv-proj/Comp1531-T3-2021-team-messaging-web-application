Assumptions
- Input types are not guaranteed to be correct. If the incorrect input type is
  given, then TypeError is thrown
- auth_id, u_id and channel_id can be any arbitrary integer, including negative
  number
    - This implementation has auth_id and channel_id iterate up from 0, while 
      u_id iterates down from 0
- For channel_messages_v1 a negative start index causes an InputError exception
- auth_register_v1 is always able create a handle, ie first_name and last_name
  at least contain one alphanumeric character
- Black box testing of channel_messages, save the case of an empty list, is not
  possible
- channel_list_v1 checks whether a user is in all_members of a channel to
  determine if it is "a part of" the channel
- If channel_list_v1 and channel_list_all_v1 cannot find any channels the user
  is a part of (or in general for channel_lsit_all_v1) it will return an empty
  list