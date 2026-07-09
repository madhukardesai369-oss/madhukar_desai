
import sys
from auth import login, seed_default_users, add_user
from rooms import add_room, show_available, list_all_rooms
from bookings import (
    book_room, cancel_booking, checkout, search_by_customer,
    list_bookings, filter_bookings, show_bill
)
from billing import generate_bill_pdf, generate_payment_qr
from analytics import show_analytics_menu, summary_stats
from reports import export_excel, export_pdf
from utils import pick_date, prompt_nonempty


BANNER = r"""
╔══════════════════════════════════════════════════════╗
║           GRAND STAY  ·  HOTEL BOOKING CLI           ║
╚══════════════════════════════════════════════════════╝
"""


def _print_menu(role):
    print("\n" + "─" * 54)
    print(f"  Role: {role.upper()}")
    print("─" * 54)
    common = [
        (" 1", "Show available rooms (today)"),
        (" 2", "Show available rooms (choose dates)"),
        (" 3", "Book a room"),
        (" 4", "Cancel booking"),
        (" 5", "Check out"),
        (" 6", "Search booking by customer name"),
        (" 7", "Display ALL booked rooms"),
        (" 8", "Filter bookings"),
        (" 9", "View bill for a booking"),
        ("10", "Generate PDF bill + QR for a booking"),
    ]
    admin_only = [
        ("11", "Add new room"),
        ("12", "List all rooms"),
        ("13", "Charts & analytics"),
        ("14", "Export report to Excel"),
        ("15", "Export report to PDF"),
        ("16", "Add new user"),
        ("17", "Show summary stats"),
    ]
    for k, v in common:
        print(f"  {k}) {v}")
    if role == "admin":
        print("  ── Admin ──")
        for k, v in admin_only:
            print(f"  {k}) {v}")
    print("   0) Logout & exit")


def main():
    print(BANNER)
    seed_default_users()
    user = login()
    if not user:
        print(" Login failed. Exiting.")
        sys.exit(1)

    while True:
        _print_menu(user["role"])
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                show_available()
            elif choice == "2":
                from datetime import date
                ci = pick_date("Check-in date")
                co = pick_date("Check-out date", min_date=ci)
                show_available(ci, co)
            elif choice == "3":
                book_room(user)
            elif choice == "4":
                cancel_booking(user)
            elif choice == "5":
                checkout(user)
            elif choice == "6":
                search_by_customer()
            elif choice == "7":
                list_bookings(status_filter="active")
            elif choice == "8":
                filter_bookings()
            elif choice == "9":
                show_bill()
            elif choice == "10":
                bid = prompt_nonempty("Booking ID: ").upper()
                from bookings import get_booking
                b = get_booking(bid)
                if not b:
                    print(" Not found.")
                else:
                    pdf = generate_bill_pdf(b)
                    qr = generate_payment_qr(b)
                    print(f"  PDF: {pdf}")
                    print(f"  QR : {qr}")
            elif choice == "11" and user["role"] == "admin":
                add_room(user)
            elif choice == "12" and user["role"] == "admin":
                list_all_rooms()
            elif choice == "13" and user["role"] == "admin":
                show_analytics_menu()
            elif choice == "14" and user["role"] == "admin":
                p = export_excel()
                print(f"  Excel saved: {p}")
            elif choice == "15" and user["role"] == "admin":
                p = export_pdf()
                print(f"  PDF saved: {p}")
            elif choice == "16" and user["role"] == "admin":
                add_user(user)
            elif choice == "17" and user["role"] == "admin":
                s = summary_stats()
                for k, v in s.items():
                    print(f"  {k:20s}: {v}")
            elif choice == "0":
                print(" Goodbye!")
                sys.exit(0)
            else:
                print(" Invalid choice or insufficient privileges.")
        except KeyboardInterrupt:
            print("\n Cancelled.")
        except Exception as e:
            print(f" Error: {e}")


if __name__ == "__main__":
    main()