"""
This module handels authentication with the TradeStation API.


Authorization Flow:
- Authorization Code: 
     Requires manual login with a web browser. 
     Expires in 20 min
- Refresh Token: 
    Requires Authorization Code.
    Only expires if invalidated by request.
- Access Token: 
     Gotten with Authorization Code or Refresh Token. 
     Used to recive data and make trasactions. 
     Expires in 20 min

Documentation for Authorization
1) https://auth0.com/docs
2) https://api.tradestation.com/docs/fundamentals/authentication/auth-overview
"""


import json
import urllib.parse
#import logging # users might find this useful for logging, but not something I have used.
import os
import secrets
from typing import Any, Callable, Dict, Union
from urllib.parse import parse_qs, urlparse
import time

import httpx
import http.server
import socketserver
import requests
import webbrowser

import ts.common_variables as vars



"""
*** Note: Defaults for all of these variables are either set in common_variables.py or ts_state.json text files
valid(
    paper_trade_provided:bool [Default is live trading  True = simulated trading, False = live trading]  "paper_trade" variable in common_variables.py
    client_key_provided:str, [Optional way to pass in client key given by TradeStation.]
    client_secret_provided:str="", [Optional way to pass in client secret given by TradeStation.]
    authorization_scope_provided:str="", [Optional way to pass in authorization scope]
    call_back_domain_provided:str="" Optional - default is set in common_variables.py
)
"""
def valid(
        paper_trade_provided:bool = vars.paper_trade,
        client_key_provided:str="", 
        client_secret_provided:str="",
        authorization_scope_provided:str="", 
        call_back_domain_provided:str="" # http://localhost:3000 will work
        ) -> bool:
    """
    Main function which confirms the client has a valid token, or attemps to get one.
    Every twenty minuets a new access token will be required.
    First login attempt requires user to login to tradestation account through a browser.
    Tradestation will then generate a URL with the key required. This script will never
    have access to the actual password/username. 

    If login is required, script will first check if function varliables have required credentials.
    It will next check for the credentials in "credentials.json
    It is accetable to provide them either way

    Returns True if client has valid token, returns False if valid token could not be retrived

    > paper_trade: bool: 
        True: will check if client has valid token and set to simulated/paper trading mode
        False: will check if client has valid token and set live trading mode
    > client_key: Optional, client key provided by Tradesation after api aproval
    > clinet_secret: Optional, client secret provided by Tradestation after api aproval
    > authorization_scope: Optional, scope of permisions needed
    > call_back_domain: Optional, a default host is used that will work. 
    """
    if(vars.ts_state_isLoaded == False): #loads information from ts_state.jason into script vars
        if(load_ts_state() == False):
            print("Could not load information from ts_state.json")
            exit()
    else:
        print("ts_state loaded")

    if(client_key_provided != "" and client_key_provided != vars.client_key):
    #Client key passed directly to function
        if(client_secret_provided == ""):
            return False # if new client key is given, a new secrent key must also be given
        else:
            vars.client_key = client_key_provided
            vars.client_secret = client_secret_provided
        vars.access_token = "" # new account given, previous access token should be removed
    if(authorization_scope_provided != "" and authorization_scope_provided != vars.authorization_scope):
        vars.authorization_scope = authorization_scope_provided
        vars.access_token = "" # need to get new access token with new scope
    if(call_back_domain_provided != ""):
        vars.call_back_domain = call_back_domain_provided
    #print("refresh token: "+vars.refresh_token)
    if(vars.refresh_token != "" and vars.refresh_token != None): 
    #If there is an access token stored, check if it is still valid
        if(vars.access_token_expires_at < time.time() or vars.access_token == ""):
            # access token is expired or does not exist
            return get_access_token()
    elif(have_credentials()):
        print("have credentials - but user will need to manually login to get refresh token")
        return get_refresh_token()
    else:
        print("Do not have client secret or key. Can not get access or refresh token")
        return False


def Revoke_Refresh_Tokens() -> bool:
    """
    Will revoke all refresh tokens even granted for this client ID.
    Use this for security purposes. If you ever suspect a refresh token has or might be 
    compremised, use this function to provent a security breach. Even if your key/secret
    are compremised, bad actors will need to also have a refresh token which requires manual 
    login to Tradestation with a web browser. *Note* This function does not invalidate
    access tokens, which expire in 20 minuets. 

        need function to invalidate all refresh tokens - make sure to remove from variables and json file.
        might also be good to have removal function of refresh token turns out not to be good
        need function to get new access token if there is 
    """
    if (have_credentials() == False):
        print("do not have information needed to revoke refresh token")
        return False
    if(vars.refresh_token == ""):
        return False # No refresh token to revoke
    #print("revoke refresh tokens")
    response = requests.post(
            vars.REVOKE_ENDPOINT,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'client_id': vars.client_key,
                'client_secret': vars.client_secret,
                'token': vars.refresh_token
            }
        )
    if(response.status_code == 200):
        #The Refresh Token is revoked, does not exist, or was not issued to the application making the revocation request. The response body is empty.
        #load ts_state to make modifications
        load_func = jason_loader(vars.path_to_JSON+"ts_state.json")
        ts_state_dict = load_func()
        ts_state_dict["refresh_token"] = ""
        #resave ts_state without refresh token
        update_token = __update_token(vars.path_to_JSON+"ts_state.json")
        update_token(ts_state_dict)    
        #update vars object.
        load_ts_state()
        return True
    elif(response.status_code == 400):
        print("Invalid request. Likely that the required parameters were not sent.")
        return False
    elif(response.status_code == 401):
        print("The request is not authorized. Check that the application credentials (client_id and client_secret) are present in the request and hold valid values.")
        return False
   

"""
Confirms that both Client ID and Client Secret are given, or tries to aquire them.
Returns true if both are present, false if they can not be aquired.
"""
def have_credentials() -> bool:
    
    if(vars.client_key != "" and vars.client_secret != "" and vars.authorization_scope != "" and vars.call_back_domain != ""):
        return True
    else:
        #attemp to get credentials from Jason File
        load_func = jason_loader(vars.path_to_JSON+"credentials.json")
        credentials_dict = load_func()
        vars.client_key = credentials_dict.get("client_key")
        vars.client_secret = credentials_dict.get("client_secret")
        vars.call_back_domain = credentials_dict.get("call_back_domain")
        vars.authorization_scope = credentials_dict.get("authorization_scope")
        #print("test client_key: "+vars.client_key)
        if(vars.client_key != "" and vars.client_secret != "" and vars.authorization_scope != "" and vars.call_back_domain != ""):
            return True
        else:
            print("json file does not have required credentials and they have not been provided.")
            return False


"""Loads items from ts_state.json into vars object. """
def load_ts_state() -> bool:  
    try:
        load_func = jason_loader(vars.path_to_JSON+"ts_state.json")
        credentials_dict = load_func()
        if(credentials_dict.get("access_token") != None):
            vars.access_token = credentials_dict.get("access_token")
        else:
            vars.access_token = ""
        if(credentials_dict.get("refresh_token") != None):   
            vars.refresh_token = credentials_dict.get("refresh_token")
        else:
            vars.refresh_token = ""
        if(credentials_dict.get("id_token") != None):
            vars.id_token = credentials_dict.get("id_token")
        else:
            vars.id_token = ""
        if(credentials_dict.get("scope") != None):
            vars.authorization_scope = credentials_dict.get("scope")
        else:
            vars.authorization_scope = 0
        if(credentials_dict.get("expires_at") != None):
            vars.access_token_expires_at = int(credentials_dict.get("expires_at"))
        else:
            vars.access_token_expires_at = 0
        vars.ts_state_isLoaded = True
    except:
        print("could not load information from ts_state.jason")
        return False


def get_authorization_code() -> bool:
    """
    Authorization code is needed to request refresh token. 
    It expires in 20 min and requires manual login on web browser. 
    Apears to only be vaid for one use. 

    Can only get authorization by manually completing the OAuth2 flow. Refresh tokens
    do not expire (unless requested) so this should only need to be done once. 

    Notes:
    - Follow the printed instructions to visit the authorization URL and paste the full redirect URL..
    """
    #print("get authorization code")
    if (have_credentials() == False):
        print("do not have information needed to manually login to aquire refresh token")
        return False
    
    # Generate the authorization URL
        # "state" = An opaque arbitrary alphanumeric string value included in the 
        # initial request that is include when redirecting back to this app. 
        # Used to prevent cross-site request forgery attacks.
        # Ideally, this should be dynamically generated for each request
    vars.state = secrets.token_hex(16)
    url = ('https://signin.tradestation.com/authorize?response_type=code&client_id={}'
       '&audience=https://api.tradestation.com&redirect_uri={}&state={}&scope={}').format(vars.client_key, vars.call_back_domain,
                                                                                  vars.state, vars.authorization_scope)

    # Open the authorization URL in Chrome
    f = open('Login_lander.html','w')
 
    message = ("""<html>
    <head></head>
    <body>
        <p>
            <b><a href="{}">THIS LINK</a></b> will take you to the TradeStation website to login. 
            </p><p>
                After logging in, the site will forward to a URL that contains the authorization token required
                to obtain a refresh token that will be used to authorize this script to use the TradeStation API.
            </p><p> 
                After logging in, the landing page will say "Unable to connect." This is normal.
            </p><p>
                This process only needs to be completed once because refresh tokens do not expire unless requested. 
        </p>
    </body>
    </html>""").format(url)
    
    f.write(message)
    f.close()
    #Change path to reflect file location
    filename = 'file:///'+os.getcwd()+'/' + 'Login_lander.html'
    
    webbrowser.open_new(filename) #open_new_tab
    try:
        try:
            port = int(vars.call_back_domain.split(":")[2])
        except:
            print("Critical error: Can not extract Port from call back domain: "+vars.call_back_domain)
            exit()
        with socketserver.TCPServer(("", port), AuthorizationCallBack) as httpd: 
            httpd.serve_forever()
    except Exception as e:
        print("failed to run local server for authorization code: ")
        print(e)
        try:
            httpd.server_close()#  provents error in which a server from a last attempt is still running
            #print("port closed")
        except:
            print("Could not shut down web server. If it remains open there is likely to be errors when the script is run.")
        exit()


# Start the HTTP server to listen for the callback
class AuthorizationCallBack(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        #**** need to figure out how to shut down web server if the url is bad. If either that user closes the window, or the url response is incorect. 
        #print("Response Handeler: "+self.path)
        url_dictionary = urllib.parse.parse_qs(self.path.split('?')[1])
        if(url_dictionary['state'][0] == vars.state):
            # go get refresh token with authorization code
            print("now getting refresh token - code: "+url_dictionary["code"][0])
            get_refresh_token(url_dictionary["code"][0])
        else:
            Warning("Recived verification code does not match. Possible cross forgery attack. Exiting script")
            exit()
        #return save_authorization_code(self.path)


def get_refresh_token(authorization_code:str = ""): # -> AsyncClient | Client
    if(authorization_code == ""):
        # Need to first get authorization code, which will call this function afterwards. 
        get_authorization_code()
    else:
        # Send a POST request to the token endpoint to obtain a refresh token
        print("start get_refresh_token")
        response = requests.post(
            vars.TOKEN_ENDPOINT,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': vars.call_back_domain,
                'client_id': vars.client_key,
                'client_secret': vars.client_secret
            }
        )
        
        token = response.json()
        print("refresh token response: "+response.text)
        if "error" in token:
            if(token['error'] == "access_denied"):
                print("Authorization token was denied. Reason given: "+token['error_description']+".  Most likely the client secret provided is incorect.")
                exit()
            elif(token['error'] == "invalid_grant"):
                print(token['error_description'])
                exit()
        #add timestamp for when access code will expire (also given with refresh token)
        token["expires_at"] = time.time() + int(token["expires_in"]) - vars.access_token_expire_margin
        update_token = __update_token(vars.path_to_JSON+"ts_state.json")
        update_token(token)    
        #update vars object.
        load_ts_state()

        # Initialize the Client
        #client_object: type[AsyncClient] | type[Client] = AsyncClient if asyncio else Client

        """
        return client_object(
            client_id=vars.client_key,
            client_secret=vars.client_secret,
            paper_trade=vars.paper_trade,
            _access_token=str(token.get("access_token")),
            _refresh_token=str(token.get("refresh_token")),
            _access_token_expires_in=int(token.get("access_token_expires_in", 0)),
            _access_token_expires_at=int(int(time.time()) + int(token.get("access_token_expires_at", 0))),
        )
        """


def get_access_token() -> bool:
    """
    Requests access token from TradeStation
    A refresh token is required for this
    Acess tokens expire in 20 minuets by default. 
    Refresh tokens never expire by default, unless a request is made to void them. 
    """
    if (have_credentials() == False):
        print("do not have information needed to manually login to aquire refresh token")
        return False
    if(vars.refresh_token == ""):
        return False # require refresh token to get access token
    print("start get_access_token")
    response = requests.post(
            vars.TOKEN_ENDPOINT,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'refresh_token',
                'client_id': vars.client_key,
                'client_secret': vars.client_secret,
                'refresh_token': vars.refresh_token
            }
        )
        
    token = response.json()
    if "error" in token:
        if(token['error'] == "access_denied"):
            print("Authorization token was denied. Reason given: "+token['error_description']+".  Most likely the client secret provided is incorect.")
            exit()
        elif(token['error'] == "invalid_grant"):
            print("Invalid grant error: "+token['error_description'])
            exit()
    #add timestamp for when access code will expire
    token["expires_at"] = time.time() + int(token["expires_in"]) - vars.access_token_expire_margin
    token["refresh_token"] = vars.refresh_token
    
    update_token = __update_token(vars.path_to_JSON+"ts_state.json")
    update_token(token)    
    #update vars object.
    load_ts_state()
    return True


def __update_token(token_path: str) -> Callable:
    """
    Return a function to update the token information and save it to a file.

    Parameters:
    - token_path (str): The path where the token information will be saved.

    Returns:
    - Callable: A function that takes a token dictionary and saves it to a file.

    Example Usage:
    ```
    update_func = __update_token("path/to/token.json")
    update_func(token_dict)
    ```

    Notes:
    - The returned function will save the token in JSON format.
    """

    def update_token(t: Any) -> None:
        """
        Update the token information and saves it to a file.

        Parameters:
        - t (Any): The token information to be saved. Could be a dictionary, list, or any serializable type.

        Returns:
        - None

        Example Usage:
        ```
        update_token(token_dict)
        ```
        Notes:
        - The function saves the token in JSON format to a file specified by `token_path`.
        """
        #print("Updating token to file %s", token_path)

        with open(token_path, "w") as f:
            json.dump(t, f, indent=4)

    return update_token


def jason_loader(file_path: str) -> Callable[[], Dict[str, Any]]:
    """
    Return a function to load the token information from a file.

    Parameters:
    - file_path (str): The path from where the token information will be loaded.

    Returns:
    - Callable: A function that loads and returns a token dictionary.

    Example Usage:
    ```
    load_func = jason_loader("path/to/token.json")
    token_dict = load_func()
    ```
    Notes:
    - The returned function will read the information from a JSON file 
      and turn it into a dictionary object.
    """

    def load_jason() -> Any:
        """
        Load the information from a .jason file and returns it as a dictionary object.

        Returns:
        - Any: The token information, typically a dictionary or list, or any deserializable type.

        Example Usage:
        ```
        token_data = load_jason()
        ```

        Notes:
        - The function reads the token from a JSON file specified by `file_path`.
        - The function uses a logger to log the path from which the token is loaded.

        Warnings:
        - The `file_path` and `get_logger()` are assumed to be available in the function's scope.

        Raises:
        - FileNotFoundError: If the specified `file_path` does not exist.
        - JSONDecodeError: If the file does not contain valid JSON data.
        """
        print("Loading token from file: " + file_path)
        #get_logger().info("Loading token from file %s", file_path)

        with open(file_path, "rb") as f:
            token_data = f.read()
            return json.loads(token_data.decode())

    return load_jason