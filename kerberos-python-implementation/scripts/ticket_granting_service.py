
"""
This file provides a helper for The ticket granting service.
Needed Information to be able to function:
    - 
    -
Expected functionalities:
    - 
"""
from db_helper import DBHelper
import requests
import time
import string
import json
import random
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES
from EncryptionHelper import EncryptionHelper
#? Importing modules:
#? DBHelper handles database access.
#? requests, time, etc., are standard Python modules.
#? Crypto.Cipher.AES will not be used directly here (encryption is handled in EncryptionHelper).
#? EncryptionHelper is a custom class for encryption/decryption.


class TicketGrantingService:
    def __init__(self,master_key):
        self.db = DBHelper()
        #? # Initialize a database connection/helper.
        self.master_key = master_key
        #? # Global key used for key wrapping/unwrapping.
        self.eh = EncryptionHelper("TicketGrantingService")
        #? Initialize encryption utility for this service.
        #? The class needs a master_key which it uses in combination with service-specific keys to encrypt/decrypt data.



    def duplicate_string(self,input_string):
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]
    #? This ensures the string is at least 16 characters long (AES block size).
    #? It duplicates the string until it’s long enough, then trims to 16 characters.

    def process(self, authenticator, tgt, tgr):
        #? The core function of the TGS. Parameters:
        #? authenticator: Encrypted data from the client.
        #? tgt: Ticket-Granting Ticket (from AS).
        #? tgr: Service request (which service the user wants to access).


        json_format = tgr.replace("'", "\"")
        tgr = json.loads(json_format)
        #? If tgr uses single quotes, replace them with double quotes so it becomes valid JSON and parse it.

        status, fetched_service = self.db.fetch_service(str(tgr.get('service_name')))
        if status == -1 : 
            return -1, fetched_service
        #? Looks up the requested service in the DB. If not found, return error.

        service_secret_key = fetched_service.get_secret_key()
        #? Get the secret key associated with the requested service (needed to encrypt the ticket for that service).
        
        if service_secret_key:
            """
            TGS need to decrypt the ticket granting ticket offered to the client by
            Authentication Server. Note, since this ticket can only be decrypted by
            TGS's secret key, not even the client can know what is inside this. So
            we need to fetch this key from the kdc database.
            """
            status, fetched_tgs = self.db.fetch_service("tgs")
            tgs_secret_key = fetched_tgs.get_secret_key()
            #? The TGS itself is also a "service" in the KDC. Fetch its secret key so it can decrypt the TGT.

            if tgs_secret_key:
                ticket_granting_ticket_plain = self.eh.decrypt(tgt, tgs_secret_key, self.master_key)
                if not ticket_granting_ticket_plain:
                    return -1, "TGT decryption failed."
                #? Use TGS’s secret key + master key to decrypt the TGT. If decryption fails, reject the request.

                print("Received TGT from Client obtained from Authentication Server")
            else:
                print("Tgs secret key or service not found")


            """
            TGS also need to decrypt the authenticator message from the client node.
            Remember, this message was encrypted using the TGS_SESSION_KEY obtained by the
            client from the Authentication Server. This TGS knows the TGS_SESSION_KEY from
            the above decryption. Now we can make use of the same to decrypt this message.
            """
            authenticator_plain = self.eh.decrypt(authenticator, ticket_granting_ticket_plain.get('tgs_session_key'), self.master_key)
            #? Authenticator was encrypted using the tgs_session_key shared with the client (retrieved from decrypted TGT). Now we decrypt it.


            # compare the username from authenticator as well as tgt
            if authenticator_plain.get('username') == ticket_granting_ticket_plain.get('username'):
                #? Username in both authenticator and TGT must match (proves both belong to the same client).

                auth_timestamp = datetime.strptime(authenticator_plain.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                tgt_timestamp = datetime.strptime(ticket_granting_ticket_plain.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                elapsed_time_in_hours = divmod((auth_timestamp - tgt_timestamp).seconds, 3600)[0]
                #? Calculate how much time has passed since TGT was issued. 
                #? Ideally, more time-based logic should be implemented here (currently it's a stub).

                if True:
                    #? Placeholder. Should be replaced with real expiration and replay check logic.
                    #? check if tgt is expired using the lifetime value of the ticket
                    #? difference of current timestamp - tgt timestamp < lifetime of ticket
                    #? check if it is already cached, if not cache it to avoid replay attacks
                    #? generate service session key
                    
                    service_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])[0:16]
                    #? Generate a new 16-char session key for communication between client and requested service.

                    service_payload = {"username": str(authenticator_plain.get('username')), 
                                       "service_id": str(tgr.get('server_id')),
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}
                    #? Data to be shared with the target service, contains username, session key, and lifetime.

                    service_ticket_encrypted = self.eh.encrypt(service_payload, service_secret_key, self.master_key)
                    #? Encrypt this using the requested service's secret key, so only it can decrypt it.

                    tgs_ack_payload = {"service_id": str(tgr.get('service_id')), 
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}
                    #? This is a confirmation back to the client. It contains the same 
                    #? service_session_key, so client can use it to talk to the service.

                    tgs_ack_encrypted = self.eh.encrypt(tgs_ack_payload, ticket_granting_ticket_plain.get('tgs_session_key'), self.master_key)
                    #? Encrypted using the TGS session key (only client can decrypt this).
                    
                    self.db.close()
                    #? Close DB connection and return both:
                    #? tgs_ack_ticket → for client
                    #? service_ticket → for service

                    print("TGS Ack and Service Ticket sent to client")
                    return 1, {"tgs_ack_ticket": tgs_ack_encrypted, 
                                    "service_ticket": service_ticket_encrypted}
            else:
                return -2 , "Access Denied"
            #? The client might be trying to use someone else’s ticket—deny the request.



        """
        #! Summary of Workflow
        
Client sends TGT, Authenticator, and TGR.

TGS:

Decrypts the TGT (using its own secret).

Decrypts the Authenticator (using session key in TGT).

Verifies timestamps and usernames.

Generates a new service session key.

Encrypts a ticket for the service and a response for the client.
        
        """
