
from datetime import date
from tabulate import tabulate
from storage import load_rooms, save_rooms, load_bookings

CATEGORIES = {
    "Standard": 1500.0,
    "Deluxe":   2500.0,
    "Suite":    4500.0,
}


def _next_room_id(rooms):
    return (max([r["id"] for r in rooms], default=0) + 1)


def add_room(current_user):
    if current_user["role"] != "admin":
        print(" Only admin can add rooms.")
        return
    rooms = load_rooms()
    print("\nCategories:")
    for i, (cat, price) in enumerate(CATEGORIES.items(), 1):
        print(f"  {i}) {cat} (base ₹{price}/night)")
    try:
        choice = int(input("Choose category (1-3): "))
        category = list(CATEGORIES.keys())[choice - 1]
    except (ValueError, IndexError):
        print(" Invalid choice.")
        return
    room_number = input("Room number (e.g. 101): ").strip()
    if any(r["room_number"] == room_number for r in rooms):
        print(" Room number already exists.")
        return
    base = CATEGORIES[category]
    override = input(f"Base price (blank = ₹{base}):").strip()
    try:
        base = float(override) if override else base
    except ValueError:
        print(" Invalid price.")
        return

    room = {
        "id": _next_room_id(rooms),
        "room_number": room_number,
        "category": category,
        "base_price": base,
    }
    rooms.append(room)
    save_rooms(rooms)
    print(f" Room {room_number} ({category}) added.")


def _room_available(room_id, ci: date, co: date, bookings):
    for b in bookings:
        if b["room_id"] != room_id:
            continue
        if b["status"] not in ("booked", "checked_in"):
            continue
        bci = date.fromisoformat(b["check_in"])
        bco = date.fromisoformat(b["check_out"])
        # overlap if not (co <= bci or ci >= bco)
        if not (co <= bci or ci >= bco):
            return False
    return True


def show_available(check_in: date = None, check_out: date = None):
    rooms = load_rooms()
    if not rooms:
        print(" No rooms in system.")
        return []
    bookings = load_bookings()

    if check_in is None:
        # available *today* (single-night stay)
        from datetime import timedelta
        check_in = date.today()
        check_out = check_in + timedelta(days=1)

    avail = []
    for r in rooms:
        if _room_available(r["id"], check_in, check_out, bookings):
            avail.append(r)

    if not avail:
        print(" No rooms available for the selected dates.")
        return []

    print(f"\nAvailable rooms ({check_in} → {check_out}):")
    print(tabulate(
        [[r["id"], r["room_number"], r["category"], f"₹{r['base_price']}"] for r in avail],
        headers=["ID", "Room #", "Category", "Base Price"], tablefmt="grid"))
    return avail


def list_all_rooms():
    rooms = load_rooms()
    if not rooms:
        print(" No rooms.")
        return
    print(tabulate(
        [[r["id"], r["room_number"], r["category"], f"₹{r['base_price']}"] for r in rooms],
        headers=["ID", "Room #", "Category", "Base Price"], tablefmt="grid"))