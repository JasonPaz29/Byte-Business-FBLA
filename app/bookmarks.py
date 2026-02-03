from flask import Blueprint, redirect, render_template, url_for, send_file, flash
from flask_login import login_required, current_user
from app.bookmark_services import add_bookmark, remove_bookmark
from app.generate_pdf import generate_bookmark_report

bp = Blueprint("bookmarks", __name__)

@bp.route("/bookmark/<int:business_id>")
@login_required
def bookmark(business_id):
    add_bookmark(current_user.id, business_id=business_id)
    return redirect(url_for("main.business_detail", business_id=business_id))

@bp.route("/unbookmark/<int:business_id>")
@login_required
def unbookmark(business_id):
    remove_bookmark(current_user.id, business_id=business_id)
    flash("Bookmark removed.", "success")
    return redirect(url_for("bookmarks.view_bookmarks"))


@bp.route("/bookmarks")
@login_required
def view_bookmarks():
    bookmarks = current_user.bookmarks
    return render_template("bookmarks.html", bookmarks=bookmarks)

@bp.route("/bookmarks/report.pdf")
@login_required
def generate_report():
    bookmarks = current_user.bookmarks
    pdf_path = generate_bookmark_report(current_user, bookmarks)
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="byte_business_bookmarks_report.pdf"
    )