"""Bill PDF generation + UPI-style QR payment code."""
from pathlib import Path
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image
)
from reportlab.lib.units import mm

OUT_DIR = Path(__file__).parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)

HOTEL_NAME = "GRAND STAY HOTEL"
HOTEL_ADDR = "12 Sunset Boulevard, Mumbai 400001 · +91-22-4000-0000"
UPI_ID = "grandstay@upi"


def generate_payment_qr(booking) -> str:
    payload = (
        f"upi://pay?pa={UPI_ID}&pn=GrandStay"
        f"&am={booking['total_amount']}&cu=INR"
        f"&tn=Booking-{booking['booking_id']}"
    )
    img = qrcode.make(payload)
    path = OUT_DIR / f"qr_{booking['booking_id']}.png"
    img.save(path)
    return str(path)


def generate_bill_pdf(booking) -> str:
    qr_path = generate_payment_qr(booking)
    path = OUT_DIR / f"bill_{booking['booking_id']}.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "t",
        parent=styles["Title"],
        textColor=colors.HexColor("#1a365d"),
        fontSize=22,
        alignment=1,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading3"],
        textColor=colors.HexColor("#2b6cb0"),
    )
    normal = styles["BodyText"]

    story = []
    story.append(Paragraph(HOTEL_NAME, title))
    story.append(Paragraph(
        HOTEL_ADDR,
        ParagraphStyle("addr", parent=normal, alignment=1, textColor=colors.grey)
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f"<b>Invoice / Bill</b> — {booking['booking_id']}", h2))

    c = booking["customer"]
    cust_table = Table([
        ["Guest Name", c["name"], "Age", c["age"]],
        ["Mobile", c["mobile"], "ID Proof", c["id_proof"]],
        ["Address", c["address"], "", ""],
    ], colWidths=[28 * mm, 60 * mm, 22 * mm, 50 * mm])
    cust_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf2f7")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#edf2f7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("SPAN", (1, 2), (3, 2)),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 5 * mm))

    stay = Table([
        ["Room", f"{booking['room_number']} ({booking['category']})",
         "Check-in", booking["check_in"]],
        ["Nights", booking["nights"], "Check-out", booking["check_out"]],
    ], colWidths=[28 * mm, 60 * mm, 22 * mm, 50 * mm])
    stay.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf2f7")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#edf2f7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    story.append(stay)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Nightly Breakdown", h2))
    br_rows = [["Date", "Price (INR)", "Modifiers"]]
    for d in booking["pricing_breakdown"]:
        br_rows.append([d["date"], f"{d['price']:.2f}", ", ".join(d["modifiers"])])
    br_rows.append(["", "TOTAL", f"INR {booking['total_amount']:.2f}"])
    br = Table(br_rows, colWidths=[35 * mm, 35 * mm, 90 * mm])
    br.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fefcbf")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(br)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("Scan to pay via UPI", h2))
    story.append(Image(qr_path, width=45 * mm, height=45 * mm))
    story.append(Paragraph(f"UPI ID: <b>{UPI_ID}</b>", normal))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "Thank you for staying with us! We hope to welcome you again soon.",
        ParagraphStyle(
            "f",
            parent=normal,
            alignment=1,
            textColor=colors.grey,
            fontName="Helvetica-Oblique",
        )
    ))
    doc.build(story)
    return str(path)