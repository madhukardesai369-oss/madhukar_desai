
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent /"data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"
ROOMS_FILE = DATA_DIR / "rooms.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_users():
    return load(USERS_FILE, [])


def save_users(users):
    save(USERS_FILE, users)


def load_rooms():
    return load(ROOMS_FILE, [])


def save_rooms(rooms):
    save(ROOMS_FILE, rooms)


def load_bookings():
    return load(BOOKINGS_FILE, [])