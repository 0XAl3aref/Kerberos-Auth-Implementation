import requests
import time
import json
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES
from EncryptionHelper import EncryptionHelper
#? Imports required libraries:
#? requests for HTTP communication with the servers.
#? time for artificial delay (e.g., sleep).
#? json, base64 for encoding/decoding.
#? datetime to timestamp messages.
#? ast for literal string conversion (though unused here).
#? Crypto.Cipher.AES for encryption (used inside EncryptionHelper).
#? EncryptionHelper is a custom class to handle AES encryption/decryption.

master_key = "S0m3MA5T3RK3YY"
EncryptionHelper = EncryptionHelper("Client")
#? master_key is a static shared key (used with AES for salting or strengthening keys).
#? Instantiates the encryption helper for the client.

def fun():
    """
    Phase 1: Contact the Authentication Server by providing the user id or client id
    along with the service (here, tgs) id to obtain ticket for.
    """


    #! construct the payload to send to authenticate server
    user_name = input("Enter user name or ID  to authenticate with: ")
    service_id = input("Service name or ID to authenticate with: ")
    #? Prompts user to enter their username and the service they want to access.

    payload = {"username": str(user_name), "service_name": str(service_id),  "lifetime_of_tgt": "2"}
    #? Constructs the payload to send to the Authentication Server. The lifetime is for the Ticket Granting Ticket (TGT).

    print("-" * 40)
    print("Authenticating with the server...")
    as_response = requests.post("http://localhost:9090/authenticate", json=payload)
    time.sleep(2)
    #? Sends the payload to AS at /authenticate. Simulates a delay for realism.

    if as_response.json().get('status') == 200:
        #? If the response is successful:

        print("Successfully Authenticated With Auth Server.")
        print("-" * 40)
        response_payload = as_response.json().get('payload')
        #? Gets the encrypted payload returned by AS.

        ack_sent = response_payload.get('ack')
        print(ack_sent)
        ticket_granting_ticket = response_payload.get('tgt')
            #? Extracts two encrypted items from AS:
        #? ack = Authentication acknowledgment for client
        #? tgt = Ticket Granting Ticket to be forwarded to TGS

        user_secret_key = input("Your Secret Key To Decrypt: ")
        #? decrypt the acknowledgement section using user secret key
    
        ack_plain = EncryptionHelper.decrypt(ack_sent, user_secret_key, master_key)
        print(ack_plain)
        #? Decrypts the ack using user's secret key and master key.

        if ack_plain is not None:
            tgs_session_key = ack_plain.get('tgs_session_key')
            print("TGS Session Key: ", tgs_session_key)
        else:
            print("Error: Decryption failed, ack_plain is None.")
        #? If decryption succeeds, extract the session key (for secure communication with the TGS).

        print("-" * 40)
        print ("Acknowledgement from Authentication Server")
        time.sleep(2)
        print("Ticket Granting Ticket from Authentication Server")
        print(ticket_granting_ticket)
        print("-" * 40)
            #? Display the output from the AS for confirmation.




        """
            Phase 2: Contact ticket granting server with the ticket granting
            ticket obtained from Authentication Server along with the id of the
            service to which the client is requesting ticket from the Ticket
            Granting Server.
            """
        auth_payload = {"username": str(user_name), "timestamp": str(datetime.now())}
        #? Constructs the payload to send to the Ticket Granting Server (TGS). It includes:
        print(ack_plain)
        auth_cipher = EncryptionHelper.encrypt(auth_payload, ack_plain.get('tgs_session_key'), master_key)
        #? Encrypts the payload using the TGS session key and master key.

        tgr_payload = {"service_name": service_id, "lifetime_of_ticket": "2"}


        payload = {"authenticator": auth_cipher, "tgr": str(tgr_payload),
                "tgt": ticket_granting_ticket}
        #?Combines:
    #? The encrypted authenticator
    #? The plaintext ticket request
    #? The encrypted TGT from ASinto one payload to send to TGS. 
    
        print ("Contacting Ticket Granting Server..."  )
        tgs_response = requests.post("http://localhost:9090/ticket", json=payload)
        #? Sends the combined payload to TGS at /ticket.

        tgs_recieved_payload = tgs_response.json().get("payload")
        if(tgs_response.json().get("status") == 200):
            #? Checks for a successful response. If yes:

            print("Recieved %s as response payload."%tgs_recieved_payload)
            #? Displays the response payload.

            tgs_ack_ticket = EncryptionHelper.decrypt(tgs_recieved_payload.get('tgs_ack_ticket'), tgs_session_key, master_key)
            #? Decrypts the TGS acknowledgement to retrieve the session key for the final service.

            service_ticket = tgs_recieved_payload.get("service_ticket")
            session_key = tgs_ack_ticket.get("service_session_key")
            #? Retrieves the service_ticket (encrypted blob to be sent to the service), 
            #? and the new session key (used for secure comm with the actual service).
            
            service_payload = {"service_ticket": service_ticket, "username": user_name}
            
            #? Here the service_ticket is the encrypted blob to be sent to the actual service.
            #? That ticket that will used to create Service Session Key.
            #? The username is also sent to the service for identification ond accountability.
            #? The service_payload is the final payload to be sent to the actual service.
            #? Builds the payload for the target service (actual service the user wanted to access in the beginning).
            print('-'*40)
            print("Contacting service with payload : %s"% str(service_payload))
            service_response = requests.post("http://localhost:9090/authenticate", json=service_payload)
            #? Sends the request to the actual service.

            print(service_response.json(), session_key)
            #? Displays the service’s response along with the service session key (you can use this for secure future communication).
            exit(1)
        else:
            print(tgs_recieved_payload.get("message"))
            #? If TGS response was unsuccessful, prints the error message.

    else:
        ack_sent= as_response.json().get('payload')["message"]
        print(ack_sent)
        while ack_sent == 'User not found.':
            fun()

fun()
"""
    
    #!   Phase 1: AS (Authentication Server)
Sends username and service ID to Authentication Server.

Receives:

A Ticket Granting Ticket (TGT)

An acknowledgment encrypted with the user’s password (containing a session key).

Decrypts the acknowledgment to extract the TGS session key.

#!      Phase 2: TGS (Ticket Granting Server)
Uses the TGS session key to encrypt an authenticator.

Sends:

The TGT

Authenticator

Service request to the TGS.

Receives:

A Service Ticket

An acknowledgment encrypted with TGS session key (contains service session key).

#!     Final Phase: Contacting the Actual Service
Sends:

The Service Ticket

Username to the actual service endpoint.

Receives the service response.

Optionally, uses the final service session key to securely communicate with the service.
    
    
"""
