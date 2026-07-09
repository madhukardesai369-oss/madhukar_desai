
import calendar
from datetime import date, timedelta


def pick_date(prompt: str, min_date: date = None) -> date:
  
    today = date.today()
    if min_date is None:
        min_date = today
    year, month = today.year, today.month

    while True:
        cal = calendar.TextCalendar(firstweekday=0)
        print("n" + "─" * 40)
        print(f"  {prompt}  (min: {min_date.isoformat()})")
        print(cal.formatmonth(year, month))
        print("Options: [n]ext month  [p]rev month  [t]ype YYYY-MM-DD  or day number")
        choice = input("> ").strip().lower()

        if choice == "n":
            month += 1
            if month > 12:
                month = 1; year += 1
            continue
        if choice == "p":
            month -= 1
            if month < 1:
                month = 12; year -= 1
            continue
        if choice.startswith("t"):
            s = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                d = date.fromisoformat(s)
            except ValueError:
                print(" Invalid format."); continue
        else:
            try:
                day = int(choice)
                d = date(year, month, day)
            except (ValueError, TypeError):
                print(" Invalid input."); continue

        if d < min_date:
            print(f" Date must be on/after {min_date.isoformat()}."); continue
        return d


def prompt_int(msg, min_v=None, max_v=None):
    while True:
        try:
            v = int(input(msg).strip())
            if min_v is not None and v < min_v: raise ValueError
            if max_v is not None and v > max_v: raise ValueError
            return v
        except ValueError:
            print(" Invalid number.")


def prompt_nonempty(msg):
    while True:
        v = input(msg).strip()
        if v:
            return v
        print(" Cannot be empty.")
