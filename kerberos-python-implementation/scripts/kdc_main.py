"""
This script is responsible for handling Authentication across a database,
using the AuthenticationServer helper class.
Also responsible for calling the methods of the TicketGrantingService Helper class.
And handling errors
Expected Functionalities:
- Generate session keys for each principal and store them.
- Call Authentication server login on recieving login request.
- Call ServiceTicketGrant in TicketGrantingService
Expected errors:
- Wrong Credentials.

"""
from authentication_server import AuthenticationServer
from db_helper import DBHelper
from ticket_granting_service import TicketGrantingService

#? Imports helper classes:
#? AuthenticationServer: handles login and initial ticket creation.
#? DBHelper: probably used inside the above classes to interact with user data (not shown here).
#? TicketGrantingService: processes ticket requests after login.

from flask import Flask, jsonify, request
import json
#? Flask: Used to expose web APIs for authentication and ticket granting.
#? jsonify: Converts Python dictionaries into proper HTTP JSON responses.
#? request: Used to read incoming HTTP POST data (e.g., login credentials).
#? json: Not directly used here, but likely used in helper classes.




master_key = "S0m3MA5T3RK3YY" 
#! Master key for the KDC That is used to encrypt/decrypt the messages
#? This is the key that is used to encrypt/decrypt the messages between the client and the server for 
#? the TGS and Authentication Server.

app = Flask(__name__)
#? Initializes the Flask app to create web routes.



AS = AuthenticationServer(master_key)
TGS = TicketGrantingService(master_key)
#!Instantiates:
#?AS: The Authentication Server, initialized with the master key.
#?TGS: The Ticket Granting Service, also using the same master key for secure communication.


@app.route('/authenticate', methods=['POST'])
def authentication_server():
    #? Defines an HTTP endpoint /authenticate to handle login requests.
    #? Accepts POST requests only (e.g., username and service name).
    
    if request.method == 'POST':
        #? Technically redundant (Flask already restricts it to POST), but adds safety.

        user_name = request.json.get('username')
        service_name = request.json.get('service_name')
        lifetime_of_tgt = request.json.get('lifetime_of_tgt')
        #? Extracts the incoming username, service name, and ticket lifetime from the JSON request.

        status, payload = AS.login(user_name,service_name,2)
        #? Calls AS.login() with:
        #? user_name, service_name
        #? (hardcoded lifetime, overriding lifetime_of_tgt?)
        #? Returns: A status code (1 = success, 0 = failure) and the result payload (e.g., encrypted ticket, keys, etc.).
        
        
        if status == 1:
            response = {"status":200, "payload": payload}
            return jsonify(response)
        #? If login succeeded, return HTTP 200 with the ticket and session info.



        else:
            response = {"status":404, "payload": {"message": "User not found."}}
            return jsonify(response)
        #? If login fails (bad username), return HTTP 404 and an error message.



@app.route('/ticket', methods=['POST'])
def ticket_granting_server():
    #? Defines another endpoint /ticket for requesting service tickets (post-login).


    if request.method == 'POST':
        #? Again, checks request method for safety.


        tgt = request.json.get("tgt")
        authenticator = request.json.get("authenticator")
        tgr = request.json.get("tgr")
        #? Extracts the encrypted TGT, the authenticator (e.g., client timestamp, ID), and TGR (possibly the requested service name or some metadata).


        status, payload = TGS.process(authenticator, tgt, tgr)
        #? Sends this data to the Ticket Granting Server, which:
        #? Verifies the TGT and authenticator.
        #? Returns a service ticket and session key, if valid.
        
        if status == 1:
            response = {"status":200, "payload": payload}
            return jsonify(response)
        #? If ticket granting succeeded, return HTTP 200 and ticket/session info.


        elif status == -1:
            response = {"status": 404, "payload": {"message":payload}}
            return jsonify(response)
        #? If user not found, send HTTP 404 with the error.


        elif status == -2:
            response = {"status": 304, "payload": {"message":payload}}
            return jsonify(response)
        #? If ticket expired or reused, return HTTP 304 (Not Modified — although this is semantically incorrect for this case).




if __name__ == '__main__':
    app.run(debug=True, port=9090)
#? Starts the Flask app in debug mode on port 9090.
#? Useful for local development and testing.

    """
    #!     What Does This Script Do?
    
This Python script implements a web-based authentication interface for a Kerberos-like system using Flask. It acts as a controller that:

Exposes two HTTP endpoints:

/authenticate: Receives login requests and uses AuthenticationServer to issue a Ticket-Granting Ticket (TGT).

/ticket: Accepts a valid TGT and an authenticator, then uses TicketGrantingService to issue a service ticket.

Uses a shared master key to simulate secure encryption/decryption of ticket data.

Handles common authentication errors, such as invalid credentials or expired tickets.

Acts as the entry point to the Kerberos-like flow, coordinating between client requests and backend cryptographic ticket issuance.
    
    """