

from fastapi import Depends


class User:
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password

users_db = [
    User("admin", "admin")
]
