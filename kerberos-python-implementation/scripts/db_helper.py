import sqlite3
from user_entity import User
from service_entity import Service
#? sqlite3: Python’s built-in library for interacting with SQLite databases.
#? User, Service: Custom classes (likely basic data models) representing a user and a service.

class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("db/users.db",check_same_thread=False)
        #? Connects to the SQLite database file located at db/users.db.
        #? check_same_thread=False allows this connection to be shared across threads (useful in web servers).
        
        cursor = self.conn.cursor()
        #? Creates a cursor object for executing SQL commands.

        try:
            cursor.execute("create table users(username UNIQUE,password)")
        except sqlite3.OperationalError:
            print("Table users already exists, continuing with previous data.")
            #? Tries to create the users table. If it already exists, prints a message and continues.

        try:
            cursor.execute("create table services(name UNIQUE,secret_key)")
        except sqlite3.OperationalError:
            print("Table services already exists, continuing with previous data.")
            #? Similarly creates the services table with a unique name and a secret_key.

            
    # Requests handling fetching
    def fetch_user(self, username):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from users where users.username = "+"'"+username+"'")
        #? Runs a SQL query to fetch a user with the provided username.

        try:
            username, password = query.fetchone()
            user = User(username, password)
            return 1, user
        #? If a match is found, it constructs a User object and returns it with a success code 1.

        except TypeError:
            return -1, "User dosen't exist."
        #? If no record is found (i.e., .fetchone() returns None), returns error code -1.


    def fetch_service(self, service_name):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from services where services.name = "+"'"+service_name+"'")
        #? Same structure as fetch_user but for services.

        try:
            service_name, secret_key = query.fetchone()
            service = Service(service_name, secret_key)
            return 1,service
        except TypeError:
            return -1, "Service not found."
        #? If service found: returns it, else: returns an error.

    

    # Requests handling insertions
    def add_user(self, username, password):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into users values ('"+username+"','"+password+"')")
        self.conn.commit()
        #? Inserts a new user record. Commits the transaction to save changes.

    def add_service(self, service, secret_key):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into services values ('"+service+"','"+secret_key+"')")
        self.conn.commit()
        #? Inserts a new service into the services table.


    # For testing purposes.
    def dummy_insert(self):
        cursor = self.conn.cursor()
        insert_query = cursor.execute("insert into users values ('hedi','hedi'), ('kawkaw','kawkaw')")
        self.conn.commit()
        #? Adds two sample/dummy users to the database for testing purposes.

    def fetch_all(self):
        cursor = self.conn.cursor()
        query = cursor.execute("select * from users")
        users = query.fetchall()
        return users
    #? Returns a list of all users in the users table.


    def delete_dummy_insert(self):
        cursor = self.conn.cursor()
        query = cursor.execute("delete from users where username ='hedi' or username='kawkaw'")
        self.conn.commit()
    def close(self):
        self.conn.close()
        #? Deletes the dummy users that were inserted using dummy_insert().

        """
        #!     What This Code Does:
        
The DBHelper class is a SQLite database handler for a simplified authentication system like Kerberos. It allows you to:

Create tables for users and services (if not already present).

Fetch user/service records.

Insert new user/service records.

Insert and delete test data.

Retrieve all users.

Cleanly close the database connection.


        """