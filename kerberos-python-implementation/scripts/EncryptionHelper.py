

from Crypto.Cipher import AES
import json
#? Crypto.Cipher.AES: From the PyCryptodome library, used for AES symmetric encryption/decryption.
#? json: To serialize and deserialize data into a format suitable for encryption (string).

def duplicate_string(string):
    while len(string) < 16:
        string += string
    return string[:16]
#? Pads the string by repeating it until it reaches at least 16 characters, then slices it to exactly 16.
#? Ensures the secret key or  Initialization Vector. is exactly 16 bytes, as required by AES.

class EncryptionHelper:
    def __init__(self, context):
        self.context = context
        #? Initializes the object with a context string
        #? (used in logs to identify the encryption process origin----->"AuthenticationService" or "Client").

    def write_to_logs(self,line):
        encryption_logs = open("scripts/logs/encryption_logs.txt","a")
        encryption_logs.writelines("[%s]"%self.context + line)
        encryption_logs.close()
        #? Appends a line of log text with the context to a file.
        #? Helps in debugging encryption/decryption processes.
        
    def encrypt(self, payload, secret_key, initial_vector):
        #? Function to encrypt a given payload using secret_key and initial_vector.

        payload_str = json.dumps(payload)
        #? Converts the Python dictionary (payload) into a JSON string so it can be encrypted (AES works on strings/bytes, not dicts).


        self.write_to_logs("Recieved %s to encrypt, using %s as secret key and %s as initial_vector. \n" % (payload_str,secret_key,initial_vector))
        #? Logs what is being encrypted, and with which key/IV.

        padded_secret_key = secret_key.ljust((len(secret_key) // 16 + 1) * 16).encode()
        padded_initial_vector = initial_vector.ljust((len(initial_vector) // 16 + 1) * 16).encode()
        #? Pads both the secret key and IV to the next multiple of 16 bytes using space characters (ljust).
        #? AES key size must be 16/24/32 bytes (for AES-128/192/256), and IV must be 16 bytes in CFB mode.
        #? Not cryptographically safe padding — only for length compliance.

        cipher = AES.new(padded_secret_key, AES.MODE_CFB, padded_initial_vector)
        #? Creates a new AES cipher in CFB mode (Cipher Feedback Mode), which turns a block cipher into a stream cipher.
        #? CFB doesn't require padding for the plaintext.
        
        encrypted_payload = cipher.encrypt(payload_str.encode())
        #? Encrypts the JSON string payload using the cipher.
        #? The result is raw bytes
                
        self.write_to_logs("Encrypted to %s .\n" % str(encrypted_payload.hex()))
        #? Logs the hex-encoded encrypted result for debugging.


        return encrypted_payload.hex()
        #? Returns the encrypted payload as a hex string (easy to store/transmit).


    def decrypt(self,payload, secret_key, initial_vector):
        #? This function reverses the encryption process — takes a hex string and decrypts it back to the original dictionary.


        self.write_to_logs("Recieved %s to decrypt, using %s as secret key and %s as initial_vector. \n" % (str(payload),secret_key,initial_vector))
        #? Logs the decryption request.


        
        if not isinstance(payload, str):
            self.write_to_logs("Error: Payload is not a string, it is %s." % type(payload))
            return None
            #? Checks that the payload is a string (since encryption returns hex strings).
            #? Logs and exits if not.
    
        try:
        # Convert the payload from hex to bytes
            payload_bytes = bytes.fromhex(payload)
        except ValueError as e:
            self.write_to_logs("Error: Invalid hex string %s." % payload)
            return None    
            #? Converts the hex string back to bytes.
            #? Handles errors if the string isn't valid hex.


        padded_secret_key = secret_key.ljust((len(secret_key) // 16 + 1) * 16).encode('utf-8')
        padded_initial_vector = initial_vector.ljust((len(initial_vector) // 16 + 1) * 16).encode('utf-8')
        #? Same padding as during encryption to reconstruct the same cipher state.

        cipher = AES.new(padded_secret_key, AES.MODE_CFB, padded_initial_vector)
        #? Recreates the same AES cipher used during encryption.

        decrypted_payload = cipher.decrypt(payload_bytes)
        #? Decrypts the byte string to get the original JSON string back.



        # Convert the decrypted payload from bytes to a JSON string
        try:
            decrypted_str = decrypted_payload.decode('utf-8')
        except UnicodeDecodeError as e:
            self.write_to_logs(f"Error: Unable to decode decrypted payload. {str(e)}")
            return None
            #? Converts the decrypted bytes to a UTF-8 string.
            #? Handles decoding errors if bytes aren't valid UTF-8.

        decrypted_dict = json.loads(decrypted_str)
        #? Converts the JSON string back to a Python dictionary.


        self.write_to_logs("Decrypted to %s .\n" % str(decrypted_dict))
        return decrypted_dict
        #? Logs the final decrypted result.
        #? Returns the dictionary to the caller
        
        """
        #!  What Does This Code Do as a Whole?
        
This script defines a Python class EncryptionHelper that provides AES encryption and decryption using Cipher Feedback Mode (CFB) from the PyCryptodome library. It allows:

Encrypting Python dictionaries using a secret key and an initialization vector (IV).

Returning the encrypted result as a hex string.

Decrypting a hex string back to its original dictionary.

Logging all encryption/decryption actions for traceability.

The class is useful in applications that:

Handle sensitive data (e.g., credentials, tokens).

Require consistent secure encryption/decryption routines.

Want traceability through context-aware logging.
        """