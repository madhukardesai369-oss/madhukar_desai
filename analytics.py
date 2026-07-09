
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from storage import load_bookings, load_rooms

OUT_DIR = Path(__file__).parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)


def _save(fig, name):
    path = OUT_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return str(path)


def chart_bookings_by_category():
    bookings = [b for b in load_bookings() if b["status"] != "cancelled"]
    counts = Counter(b["category"] for b in bookings)
    if not counts:
        print(" No data.")
        return
    fig, ax = plt.subplots(figsize=(6, 5))
    colors_ = ["#4299e1", "#48bb78", "#ed8936"]
    ax.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%",
           colors=colors_, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title("Bookings by Category")
    return _save(fig, "chart_bookings_by_category.png")


def chart_revenue_by_month():
    rev = defaultdict(float)
    for b in load_bookings():
        if b["status"] == "cancelled":
            continue
        m = b["check_in"][:7]  # YYYY-MM
        rev[m] += b["total_amount"]
    if not rev:
        print(" No data.")
        return
    months = sorted(rev.keys())
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(months, [rev[m] for m in months], color="#2b6cb0")
    ax.set_title("Revenue by Month")
    ax.set_ylabel("INR")
    ax.set_xlabel("Month")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "chart_revenue_by_month.png")


def chart_occupancy_rate():
    rooms = load_rooms()
    if not rooms:
        print(" No rooms.")
        return
    occ = defaultdict(int)
    for b in load_bookings():
        if b["status"] == "cancelled":
            continue
        m = b["check_in"][:7]
        occ[m] += b["nights"]
    if not occ:
        print(" No data.")
        return
    months = sorted(occ.keys())
    total_rooms = len(rooms)
    # rough occupancy = booked-nights / (rooms * 30)
    rate = [min(100, (occ[m] / (total_rooms * 30)) * 100) for m in months]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(months, rate, marker="o", color="#e53e3e", linewidth=2)
    ax.set_title("Occupancy Rate (%) by Month")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.grid(alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "chart_occupancy_rate.png")


def show_analytics_menu():
    while True:
        print("\n── ANALYTICS ──")
        print(" 1) Bookings by category (pie)")
        print(" 2) Revenue by month (bar)")
        print(" 3) Occupancy rate (line)")
        print(" 4) Generate ALL")
        print(" 0) Back")
        c = input("> ").strip()
        if c == "1":
            p = chart_bookings_by_category()
            p and print(f"  Saved: {p}")
        elif c == "2":
            p = chart_revenue_by_month()
            p and print(f"  Saved: {p}")
        elif c == "3":
            p = chart_occupancy_rate()
            p and print(f"  Saved: {p}")
        elif c == "4":
            for fn in (chart_bookings_by_category, chart_revenue_by_month,
                       chart_occupancy_rate):
                p = fn()
                if p:
                    print(f"  Saved: {p}")
        elif c == "0":
            return
        else:
            print(" Invalid.")


def summary_stats():
    bookings = load_bookings()
    active = [b for b in bookings if b["status"] in ("booked", "checked_in")]
    completed = [b for b in bookings if b["status"] == "checked_out"]
    cancelled = [b for b in bookings if b["status"] == "cancelled"]
    revenue = sum(b["total_amount"] for b in bookings if b["status"] != "cancelled")
    return {
        "total_bookings": len(bookings),
        "active": len(active),
        "completed": len(completed),
        "cancelled": len(cancelled),
        "total_revenue": round(revenue, 2),
        "total_rooms": len(load_rooms()),
    }