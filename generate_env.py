import getpass
import os
import shutil
import time

from votx.security import hash_password

if os.path.isfile(".env") or os.path.isfile("db.env"):
    print(".env or db.env file does already exist!")
    if input("Recreate? [y|N] ") != "y":
        quit()
    if os.path.isfile(".env"):
        shutil.copy2(".env", ".env." + str(int(time.time())) + ".bak")
    if os.path.isfile("db.env"):
        shutil.copy2("db.env", "db.env." + str(int(time.time())) + ".bak")

with open(".env", "w") as f:
    url = input("URL for votx instance: ")
    dev_mode = input("Development Mode? [y|N]").lower() == "y"
    password = getpass.getpass("Enter admin password: ")
    salt = os.urandom(20)
    hashed_password = hash_password(password, salt)

    f.write("ADMIN_PASSWORD_HASH=" + hashed_password + "\n")
    f.write("ADMIN_PASSWORD_SALT=" + salt.hex() + "\n")
    f.write("SECRET_KEY=" + os.urandom(64).hex() + "\n")
    f.write("ALGORITHM=HS256\n")
    f.write('URL="' + url + '"\n')
    if dev_mode:
        f.write("DB_HOST=" + "localhost" + "\n")
    else:
        f.write("DB_HOST=" + "votx_db" + "\n")
    f.write("DB_PORT=5432\n")

with open("db.env", "w") as f:
    f.write("POSTGRES_USER=votx\n")
    f.write("POSTGRES_DB=votx\n")
    if dev_mode:
        f.write("POSTGRES_PASSWORD=strong-password\n")
    else:
        f.write("POSTGRES_PASSWORD=" + os.urandom(30).hex() + "\n")
    f.write("PGUSER=votx\n")
