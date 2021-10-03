# Assumptions

- Input types are not guaranteed to be correct. If the incorrect input type is
  given, then TypeError is thrown.
- auth_id, u_id and channel_id can be any arbitrary integer, including negative
  integers.
  - This implementation has auth_id and channel_id iterate up from 0, with u_id being
  the same as auth_id.
- The order of the lists don't matter in all_members or channel_list.
- Black box testing of channel_messages, save the case of an empty list, is not
  possible
- If channel_list_v1 and channel_list_all_v1 cannot find any channels the user
  is a part of (or in general for channel_lsit_all_v1) it will return an empty
  list
- lists including all_members and owner_members have an arbitrary order of items.
