import getpass
import os
import shutil
import time

from votx.security import hash_password

if os.path.isfile(".env"):
    print(".env file does already exist!")
    if (input("Recreate? [y|N] ") != "y"):
        quit()
    shutil.copy2(".env", ".env." + str(int(time.time())) + ".bak")

with open(".env", "w") as f:
    password = getpass.getpass("Enter admin password: ")
    salt = os.urandom(20)
    hashed_password = hash_password(password, salt)

    f.write("ADMIN_PASSWORD_HASH=" + hashed_password + "\n")
    f.write("ADMIN_PASSWORD_SALT=" + salt.hex() + "\n")
    f.write("SECRET_KEY=" + os.urandom(64).hex() + "\n")
    f.write("ALGORITHM=HS256\n")
    