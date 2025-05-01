import sqlite3


class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("db/users.db", check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        print("Existing users:", users)

# Check existing services
        cursor.execute("SELECT * FROM services;")
        services = cursor.fetchall()
        print("Existing services:", services)
        try:
            cursor.execute("create table users(username UNIQUE, password)")
            print("Users table created successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error creating users table: {e}")
        
        try:
            cursor.execute("create table services(name UNIQUE, secret_key)")
            print("Services table created successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error creating services table: {e}")
    
    def add_user(self, username, password):
        try:
            self.cursor = self.conn.cursor()

            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            
            self.conn.commit()
            print(f"User '{username}' added successfully.")
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists.")

    def add_service(self, name, secret_key):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute("INSERT INTO services (name, secret_key) VALUES (?, ?)", (name, secret_key))
            self.conn.commit()
            print(f"Service '{name}' added successfully.")
        except sqlite3.IntegrityError:
            print(f"Service '{name}' already exists.")

    def show_users(self):
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        print("Existing users:", users)

    def show_services(self):
        self.cursor.execute("SELECT * FROM services")
        services = self.cursor.fetchall()
        print("Existing services:", services)
        
        self.conn.commit() #! Commit any changes after table creation into the database

db=DBHelper()
db.add_user("saber", "MohamedSaber")
db.add_user("omar", "OmarMomen")
db.show_users()
db.add_service("powershell", "ps.pass")
db.add_service("vBox", "vBox.pass")