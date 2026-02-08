"""Informational pages: About, Privacy Policy, Terms of Service."""

from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@bp.route("/privacy")
def privacy():
    """Privacy policy page."""
    return render_template("privacy.html")


@bp.route("/terms")
def terms():
    """Terms of service page."""
    return render_template("terms.html")
