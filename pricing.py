
from datetime import date, timedelta
from storage import load_rooms, load_bookings

# Peak months (Dec, Jan, Apr, May) = +25%, off-peak (Jun, Jul, Aug) = -10%
PEAK_MONTHS = {12, 1, 4, 5}
OFF_PEAK_MONTHS = {6, 7, 8}

WEEKEND_SURCHARGE = 0.15   # +15% on Fri/Sat/Sun
OCCUPANCY_THRESHOLD = 0.70 # >70% occupied -> surge
OCCUPANCY_SURGE = 0.20     # +20%


def _daterange(d1: date, d2: date):
    days = (d2 - d1).days
    for i in range(days):
        yield d1 + timedelta(days=i)


def occupancy_on(day: date) -> float:
    rooms = load_rooms()
    bookings = load_bookings()
    if not rooms:
        return 0.0
    active = 0
    for b in bookings:
        if b["status"] not in ("booked", "checked_in"):
            continue
        ci = date.fromisoformat(b["check_in"])
        co = date.fromisoformat(b["check_out"])
        if ci <= day < co:
            active += 1
    return active / len(rooms)


def price_for_stay(base_price: float, check_in: date, check_out: date) -> dict:
    breakdown = []
    total = 0.0
    for d in _daterange(check_in, check_out):
        p = base_price
        multipliers = []

        # Seasonal
        if d.month in PEAK_MONTHS:
            p *= 1.25
            multipliers.append("peak+25%")
        elif d.month in OFF_PEAK_MONTHS:
            p *= 0.90
            multipliers.append("off-peak-10%")

        # Weekend (Fri=4, Sat=5, Sun=6)
        if d.weekday() >= 4:
            p *= (1 + WEEKEND_SURCHARGE)
            multipliers.append(f"weekend+{int(WEEKEND_SURCHARGE * 100)}%")

        # Occupancy
        occ = occupancy_on(d)
        if occ > OCCUPANCY_THRESHOLD:
            p *= (1 + OCCUPANCY_SURGE)
            multipliers.append(f"occupancy+{int(OCCUPANCY_SURGE * 100)}%")

        breakdown.append({
            "date": d.isoformat(),
            "price": round(p, 2),
            "modifiers": multipliers or ["base"]
        })
        total += p
    return {"breakdown": breakdown, "total": round(total, 2), "nights": len(breakdown)}
