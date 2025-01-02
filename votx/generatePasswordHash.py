import getpass
import os

from security import hash_password

password = getpass.getpass("Enter password: ")
salt = os.urandom(20)

hashed_password = hash_password(password, salt)

print("Salt:", salt.hex())
print("Password Hash:", hashed_password)