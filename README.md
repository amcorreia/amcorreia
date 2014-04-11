# Openfire cli


To list all messages from a specific JID.
````shell
$ ofhistdel.py list user@example.com
````

With a specific date.
````shell
$ ofhistdel.py list user@example.com date_begin 01/08/2013 date_end 02/08/2013
````

...and hour.
````shell
$ ofhistdel.py list user@example.com date_begin 01/08/2013 date_end "02/08/2013 13:37"
````

To delete all messages
````shell
$ ofhistdel.py delete user@example.com
````

delete command don't accept date option.
