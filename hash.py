import hashlib
import secrets
import datetime
from random import randint

def get_sects():
    return str(secrets.token_hex(randint(1, 16)))

def get_time():
    current_time = datetime.datetime.now()
    current_time_seconds = (current_time - datetime.datetime(1970, 1, 1)).total_seconds()
    return str(current_time_seconds)

def custom_hash(data):
    h = hashlib.new('sha256') 
    h.update((str(data) + get_sects() + get_time() + "Diyarbek Oralbaev").encode())
    return h.hexdigest()
