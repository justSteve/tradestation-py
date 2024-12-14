"""
GETTING STARTED
This is an example script to show how to use this library
* Make sure to first enter credentials into secret.credentials.json *
"""

import ts.connection as connection

""" 
Valid() checks to see if the script has everything needed to send verified commands.
If not, it will try to establish a valid connection. Returns true if there is a valid
connection, and false if it could not achive a connection. This is important becaues
the keys used to send commands are only valid for 20 minuets before a new one needs to 
be requested. 
It is a good idea to call this function as a condition before any commands.
"""
print("Getting Started")
connection.valid()
print("..")
"""
Revoke_Refresh_Tokens will remove all refresh tokens an provent access to your TradeStation 
acount without manually logging in with a web browser again. 
"""
#connection.Revoke_Refresh_Tokens() 
