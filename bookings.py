import uuid
from datetime import date, datetime
from tabulate import tabulate
from storage import load_rooms, load_bookings, save
from rooms import show_available, _room_available
from pricing import price_for_stay
from utils import pick_date, prompt_nonempty, prompt_int


def _get_room(room_id):
    for r in load_rooms():
        if r["id"] == room_id:
            return r
    return None


def book_room(current_user):
    print("\n--- NEW BOOKING ---")
    check_in = pick_date("Pick CHECK-IN date")
    check_out = pick_date("Pick CHECK-OUT date", min_date=check_in)
    if check_out <= check_in:
        print(" Check-out must be after check-in.")
        return

    avail = show_available(check_in, check_out)
    if not avail:
        return
    room_id = prompt_int("Enter Room ID to book: ")
    room = _get_room(room_id)
    if not room or room not in avail:
        print(" Invalid or unavailable room.")
        return

    print("\nCustomer details:")
    name = prompt_nonempty("  Name: ")
    age = prompt_int("  Age: ", min_v=1, max_v=120)
    mobile = prompt_nonempty("  Mobile number: ")
    id_proof = prompt_nonempty("  ID proof (Aadhaar/Passport/DL no.): ")
    address = prompt_nonempty("  Address: ")

    pricing = price_for_stay(room["base_price"], check_in, check_out)

    booking = {
        "booking_id": "BK-" + uuid.uuid4().hex[:8].upper(),
        "room_id": room["id"],
        "room_number": room["room_number"],
        "category": room["category"],
        "customer": {
            "name": name,
            "age": age,
            "mobile": mobile,
            "id_proof": id_proof,
            "address": address,
        },
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "nights": pricing["nights"],
        "base_price": room["base_price"],
        "pricing_breakdown": pricing["breakdown"],
        "total_amount": pricing["total"],
        "status": "booked",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "created_by": current_user["username"],
        "checkout_at": None,
    }
    bookings = load_bookings()
    bookings.append(booking)
    save(bookings)

    print("\n Booking confirmed!")
    print(tabulate([[
        booking["booking_id"], name, room["room_number"], room["category"],
        check_in, check_out, pricing["nights"], f"₹{pricing['total']}"
    ]], headers=["Booking ID", "Customer", "Room", "Cat", "In", "Out", "Nights", "Total"],
        tablefmt="grid"))
    return booking


def cancel_booking(current_user):
    bid = prompt_nonempty("Enter Booking ID to cancel: ").upper()
    bookings = load_bookings()
    for b in bookings:
        if b["booking_id"] == bid:
            if b["status"] in ("cancelled", "checked_out"):
                print(f" Cannot cancel a {b['status']} booking.")
                return
            b["status"] = "cancelled"
            b["cancelled_at"] = datetime.now().isoformat(timespec="seconds")
            save(bookings)
            print(f" Booking {bid} cancelled.")
            return
    print(" Booking not found.")


def checkout(current_user):
    bid = prompt_nonempty("Enter Booking ID to check out: ").upper()
    bookings = load_bookings()
    for b in bookings:
        if b["booking_id"] == bid:
            if b["status"] == "checked_out":
                print(" Already checked out.")
                return
            if b["status"] == "cancelled":
                print(" Cannot check out a cancelled booking.")
                return
            b["status"] = "checked_out"
            b["checkout_at"] = datetime.now().isoformat(timespec="seconds")
            save(bookings)
            print(f" Booking {bid} checked out. Total: ₹{b['total_amount']}")
            from billing import generate_bill_pdf, generate_payment_qr
            gen = input("Generate PDF bill + QR? (y/n): ").strip().lower()
            if gen == "y":
                pdf = generate_bill_pdf(b)
                qr = generate_payment_qr(b)
                print(f"    PDF:  {pdf}")
                print(f"    QR :  {qr}")
            return
    print(" Booking not found.")


def search_by_customer():
    q = prompt_nonempty("Customer name (partial ok): ").lower()
    matches = [b for b in load_bookings() if q in b["customer"]["name"].lower()]
    if not matches:
        print(" No matching bookings.")
        return
    _print_bookings(matches)


def list_bookings(status_filter=None):
    """Show bookings. status_filter: 'booked' | 'checked_in' | 'checked_out' | 'cancelled' | None"""
    bookings = load_bookings()
    if status_filter == "active":
        bookings = [b for b in bookings if b["status"] in ("booked", "checked_in")]
    elif status_filter:
        bookings = [b for b in bookings if b["status"] == status_filter]
    if not bookings:
        print(" No bookings match.")
        return
    _print_bookings(bookings)


def filter_bookings():
    print("\nFilter by:")
    print(" 1) Status")
    print(" 2) Category")
    print(" 3) Date range")
    print(" 4) Room number")
    c = input("> ").strip()
    all_b = load_bookings()
    if c == "1":
        s = prompt_nonempty("Status (booked/checked_out/cancelled): ").lower()
        res = [b for b in all_b if b["status"] == s]
    elif c == "2":
        cat = prompt_nonempty("Category (Standard/Deluxe/Suite): ")
        res = [b for b in all_b if b["category"].lower() == cat.lower()]
    elif c == "3":
        d1 = pick_date("From date", min_date=date(2000, 1, 1))
        d2 = pick_date("To date", min_date=d1)
        res = [b for b in all_b
               if date.fromisoformat(b["check_in"]) <= d2
               and date.fromisoformat(b["check_out"]) >= d1]
    elif c == "4":
        rn = prompt_nonempty("Room number: ")
        res = [b for b in all_b if b["room_number"] == rn]
    else:
        print(" Invalid.")
        return
    if not res:
        print(" Nothing matched.")
        return
    _print_bookings(res)


def _print_bookings(bookings):
    rows = [[
        b["booking_id"], b["customer"]["name"], b["customer"]["mobile"],
        b["room_number"], b["category"],
        b["check_in"], b["check_out"], b["nights"],
        f"₹{b['total_amount']}", b["status"]
    ] for b in bookings]
    print(tabulate(rows, headers=[
        "ID", "Customer", "Mobile", "Room", "Cat", "In", "Out", "N", "Total", "Status"
    ], tablefmt="grid"))


def get_booking(bid):
    for b in load_bookings():
        if b["booking_id"] == bid.upper():
            return b
    return None


def show_bill():
    bid = prompt_nonempty("Enter Booking ID for bill: ").upper()
    b = get_booking(bid)
    if not b:
        print(" Not found.")
        return
    print("\n" + "=" * 60)
    print(f"  BILL - {b['booking_id']}")
    print("=" * 60)
    c = b["customer"]
    print(f"  Customer : {c['name']} (Age {c['age']})")
    print(f"  Mobile   : {c['mobile']}")
    print(f"  ID Proof : {c['id_proof']}")
    print(f"  Address  : {c['address']}")
    print(f"  Room     : {b['room_number']} ({b['category']})")
    print(f"  Stay     : {b['check_in']} → {b['check_out']} ({b['nights']} nights)")
    print("-" * 60)
    print("  Pricing breakdown:")
    for d in b["pricing_breakdown"]:
        print(f"    {d['date']}  ₹{d['price']:>10}   [{', '.join(d['modifiers'])}]")
    print("-" * 60)
    print(f"  {'TOTAL':>50}  ₹{b['total_amount']}")
    print(f"  Status: {b['status']}")
    print("=" * 60)
    return b