
import bcrypt
import getpass
from storage import load_users, save_users


def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _check(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def seed_default_users():
    """Seed admin/admin and receptionist/receptionist if empty."""
    users = load_users()
    if users:
        return
    users = [
        {"username": "admin", "password": _hash("admi"), "role": "admin"},
        {"username": "receptionist", "password": _hash("receptionist"), "role": "receptionist"},
    ]
    save_users(users)
    print("[seed] Default users created:")
    print("       admin        / admin        (role: admin)")
    print("       receptionist / receptionist (role: receptionist)")


def login():
    """Prompt username/password. Return user dict or None."""
    print ("/n" + "=" * 50)
    print("           HOTEL BOOKING SYSTEM - LOGIN")
    print("=" * 50)
    users = load_users()
    for attempt in range(3):
        username = input("Username: ").strip()
        try:
            password = getpass.getpass("Password: ")
        except Exception:
            password = input("Password: ")
        for u in users:
            if u["username"] == username and _check(password, u["password"]):
                print(f"\n Welcome, {username}! (role: {u['role']})\n")
                return u
        print(f" Invalid credentials. Attempts left: {2 - attempt}\n")
    return None


def add_user(current_user):
    """Only admin can add users."""
    if current_user["role"] != "admin":
        print(" Only admin can add users.")
        return
    username = input("New username: ").strip()
    users = load_users()
    if any(u["username"] == username for u in users):
        print(" Username already exists.")
        return
    password = getpass.getpass("New password: ")
    role = input("Role (admin/receptionist): ").strip().lower()
    if role not in ("admin", "receptionist"):
        print(" Invalid role.")
        return
    users.append({"username": username, "password": _hash(password), "role": role})
    save_users(users)
    print(f" User '{username}' added.")
