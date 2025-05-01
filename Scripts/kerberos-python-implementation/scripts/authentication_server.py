"""

 Authentication Server
    - receives:
      - plaintext request for ticket granting ticket (username, name_of_service_requesting, nw_address, lifetime_of_tgt)
    - process:
      - checks whether the given username is in the kdc database (no credential check, only username lookup)
      - if success:
        - generates a random key called SESSION KEY for use between client and TGS.
    - sends:
        - Ticket_Granting_Ticket = ENC(TGS_SECRET_KEY, (username, name_of_service_requested, timestamp, nw_address, lifetime_of_tgt, TGS_SESSION_KEY))
        - Authentication_ACK = ENC(CLIENT_SECRET_KEY, (name_of_service_requested, timestamp, lifetime_of_tgt, TGS_SESSION_KEY))
        - [Authentication_ACK_ENCRYPTED, Ticket_Granting_Ticket_ENCRYPTED]
"""
from db_helper import DBHelper 
#? Imports a custom class that handles interaction with the local database
#? (likely containing user and service info).

import random
import string
import json
import base64
from datetime import datetime
#! Standard Python libraries:
#? random, string ----> used to generate a secure session key.
#? json, base64 –-----> used for data formatting (possibly for network transmission).
#? datetime –---------> for timestamping tickets.


from Crypto.Cipher import AES
#? Imports the AES encryption algorithm from pycryptodome, used to securely encrypt data.

from EncryptionHelper import EncryptionHelper
#? Imports a custom class that wraps the AES encryption logic, helping encrypt/decrypt payloads easily.

class AuthenticationServer:
    #? Defines the AuthenticationServer class 
    #? the core Kerberos------>like component responsible for authenticating clients and issuing TGTs.
    
    def __init__(self, masterkey):
        #? Initializes the server. It takes one argument: masterkey, which is used for encryption.

        self.db = DBHelper()
        #? Instantiates a DBHelper object to access users and services from the database.

        self.masterkey = masterkey
        #? Stores the master encryption key that the server will use.

        self.eh = EncryptionHelper("AuthenticationService")
        #? Creates an EncryptionHelper for this service, possibly logging the identity or initializing encryption context.
        
    def duplicate_string(self,input_string):
        #? A helper function to make sure strings used in AES encryption are at least 16 bytes long.
        #? AES requires input to be a multiple of 16 bytes, so this function duplicates the string until it reaches that length.
        
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]
        #? It duplicates the input string until it's 16+ characters, then slices it to exactly 16. AES requires 16-byte keys.
           
    def login(self,username, service, lifetime_of_tgt=10000000):
        #?Main method to authenticate a client. Takes:
#? username------> the user requesting access
#? service------->name of service user wants to access
#? lifetime_of_tgt----------> validity period for the ticket (default----> large number)

        status, response = self.db.fetch_user(username)
        #? Fetches the user’s record from the DB. If found,
        #? status == 1, and response contains user data.

        if status == 1:
            #? That bloc of code Proceeds only if user exists in the DB.
            # Get TGS info.
            status , tgs_service = self.db.fetch_service("tgs")
            #? Fetches the tgs service from the DB (TGS = Ticket Granting Service).

            tgs_secret_key = tgs_service.get_secret_key()
            #? Extracts the secret key shared between AS and TGS – used to encrypt the TGT.

            user_tgs_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])[0:16]
            #? Generates a random 16-character session key (used between client and TGS). Only letters and digits.

            auth_ack_payload = {"service_id": "tgs", "timestamp": str(datetime.now()), 
            "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}
            #? This dictionary is for the client. It tells the client:
# ?This is for the tgs
#? When it was issued
#? How long it's valid
#? The session key to use when talking to TGS
            
            tgt_payload = {"username": str(username), "service_id": str(service), "timestamp": str(datetime.now()), 
               "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}
            #?This is the actual TGT (Ticket Granting Ticket), 
            #? meant to be sent to TGS by the client later. It is encrypted so only TGS can read it.

            ticket_granting_ticket = self.eh.encrypt(tgt_payload, tgs_secret_key, self.masterkey)
            #? Encrypts the TGT with the TGS's secret key, using the master key as a salt or part of the logic.

            auth_ack = self.eh.encrypt(auth_ack_payload, response.get_password(), self.masterkey)
            #? Encrypts the acknowledgment payload with the client’s password, so only the client can decrypt it.

            final_payload = {"ack": auth_ack, "tgt": ticket_granting_ticket}
            #? Combines both into one dictionary (likely to send over the network).

            return 1, final_payload
        #? Success: returns 1 and the encrypted payload.

        else : 
            return -1,"User not found."
        #? If user doesn't exist, return an error.

        """
        #!                What This Code Does 
        
This code defines an Authentication Server (AS) component in a Kerberos-like authentication system. It:

Receives a login request from a client with a username and requested service.

Verifies the user exists (no password check yet).

Fetches the TGS secret key from the database.

Generates a session key to be used between the client and TGS.

Creates two encrypted objects:

Ticket Granting Ticket (TGT): only TGS can decrypt.

Authentication Acknowledgment: only the client can decrypt.

Returns both to the client so they can request a service ticket from TGS later.

This mirrors the first step of the Kerberos protocol, which sets up secure authentication between a client and the TGS.

        """
