#? This script defines a User class that represents a user entity in the system.
class User:
    #? This declares a class named User. It is used to represent a single user in the system.
    #? In the context of authentication (like Kerberos), this object could be used to store 
    #? credentials before validating or storing them securely.
  
    def __init__(self, username, password):
        self.username = username
        self.password = password
        #? The __init__ method is the constructor. It is called when a User object is created.
        #? username: The name/ID of the user.
        #? password: The user’s password in plaintext (note: in real secure systems, you would never store or handle passwords like this — they would be hashed).
        #? self.username and self.password are instance variables that store the provided values.
        
    def get_username(self):
        return self.username
    #? This is a getter method for accessing the user's username.
    #? It allows other parts of the code to retrieve the username without 
    #? directly accessing the self.username variable.

    def get_password(self):
        return self.password
    #? This is a getter method for accessing the user's password.


        