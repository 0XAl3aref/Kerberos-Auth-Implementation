"""
This script launchs a service that exposes endpoints 

"""
from flask import Flask, jsonify, request
import json
from datetime import datetime
from EncryptionHelper import EncryptionHelper
#? Flask: Used to build the web API.
#? json: Included to handle JSON serialization (though not directly used here).
#? datetime: Used to handle timestamps, though the time validation line is commented out.
#? EncryptionHelper: A custom class (from your previous code) that handles AES encryption/decryption and logging.

master_key = "S0m3MA5T3RK3YY"
service_secret_key = "secretsecret"
#? master_key: The initial vector (IV) used in decryption, shared between the client and this protected service.
#? service_secret_key: The AES secret key specific to this service, used to decrypt the ticket.
#? These two values are used by EncryptionHelper to decrypt incoming encrypted data (like the service ticket).

app = Flask(__name__)
#? Initializes the Flask app for routing HTTP requests.


eh = EncryptionHelper("ProtectedService")
#? Creates an instance of EncryptionHelper, initialized with the context "ProtectedService".
#? This context will appear in the log entries to help trace which component is 
#? performing encryption/decryption operations.

@app.route('/authenticate', methods=['POST'])
def protected():
#? Defines a route /authenticate for POST requests.
#? This simulates a protected service that needs to verify a service ticket before providing access.


    if request.method == 'POST':
    #? Validates that the request method is POST (though Flask already restricts it with methods=['POST']).


        st = request.json.get('service_ticket')
        #? Reads the service_ticket field from the JSON request body.
        #? This is expected to be an encrypted string.
        
        st_plain = eh.decrypt(st, service_secret_key, master_key)
        #? Decrypts the service ticket using:
        #? service_secret_key: Used as the AES key.
        #? master_key: Used as the initialization vector (IV).
        #? The result st_plain is expected to be a Python dictionary with keys like username, timestamp, lifetime_of_ticket, and service_session_key.
        
        
        if st_plain.get("username") == request.json.get("username") :
            #? Verifies that the username in the decrypted service ticket matches the username provided by the client in the JSON request.
            #? This ensures the ticket belongs to the correct user.
            
            response = {"status": 204, "payload":"Authenticated and the service and client session key is %s"%st_plain.get("service_session_key")}
            return jsonify(response)
        #? If the username matches:
        #? Returns HTTP 204 (No Content) with a message that includes the session key used for communication between client and service.
        #? Though 204 typically means “no content,” this API is sending a payload, which is unconventional but functional.
        
        else: 
            response = {"status": 301, "payload":"Unauthorized"}
            return jsonify(response)
        #? If the username does not match, return:
        #? HTTP 301 (Moved Permanently) with a message "Unauthorized".
        #? Technically wrong status code for authorization issues — should be 401 Unauthorized.

if __name__ == '__main__':
    app.run(debug=True, port=9090)
    #? Runs the Flask app on localhost:9090 in debug mode.

    """
    #!        What Does This Script Do?
    
This script simulates a protected service endpoint that authenticates clients using a service ticket, in a Kerberos-like authentication system.

Here's what it does:
Receives encrypted service tickets from clients via the /authenticate endpoint.

Decrypts the service ticket using the EncryptionHelper and validates:

The username in the ticket matches the username in the request.

If valid:

It returns a response indicating successful authentication and shares the client-service session key.

If invalid:

It denies access with an "Unauthorized" message.


    """
