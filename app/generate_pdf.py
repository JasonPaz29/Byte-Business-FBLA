from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_bookmark_report(user, bookmarks) -> BytesIO:
    """
    Returns a BytesIO containing a PDF report of the user's bookmarks.
    `bookmarks` should be a list of Business objects.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Header ---
    y = height - 60
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Byte Business — Bookmarks Report")

    y -= 22
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"User: {getattr(user, 'username', 'Unknown')}")
    y -= 15
    c.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # --- Summary stats ---
    y -= 25
    total = len(bookmarks)

    # category counts
    category_counts = {}
    for b in bookmarks:
        cat = (getattr(b.business, "category", None) or "Uncategorized").strip()
        category_counts[cat] = category_counts.get(cat, 0) + 1

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Summary")
    y -= 16
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Total bookmarks: {total}")
    y -= 14

    # Print top categories (up to 6)
    if total > 0:
        top_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        c.drawString(50, y, "Bookmarks by category:")
        y -= 14
        for cat, count in top_cats:
            c.drawString(70, y, f"- {cat}: {count}")
            y -= 14
    else:
        c.drawString(50, y, "No bookmarks yet.")
        y -= 14

    # --- Table header ---
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Bookmarked Businesses")
    y -= 18

    # Column headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Name")
    c.drawString(260, y, "Category")
    c.drawString(360, y, "Location")
    y -= 12
    c.line(50, y, width - 50, y)
    y -= 14

    c.setFont("Helvetica", 10)

    def new_page():
        nonlocal y
        c.showPage()
        y = height - 60
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Byte Business — Bookmarks Report (cont.)")
        y -= 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Name")
        c.drawString(260, y, "Category")
        c.drawString(360, y, "Location")
        y -= 12
        c.line(50, y, width - 50, y)
        y -= 14
        c.setFont("Helvetica", 10)

    # Rows
    for b in bookmarks:
        if y < 70:  # bottom margin
            new_page()

        name = (getattr(b.business, "name", "") or "")[:36]
        cat = (getattr(b.business, "category", "") or "")[:16]
        loc = (getattr(b.business, "location", "") or "")[:22]

        c.drawString(50, y, name)
        c.drawString(260, y, cat)
        c.drawString(360, y, loc)
        y -= 14

    c.save()
    buffer.seek(0)
    return buffer
