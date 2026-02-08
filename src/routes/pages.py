"""Informational pages: About, Privacy Policy, Terms of Service."""

from flask import Blueprint, render_template, make_response, current_app, url_for
from datetime import datetime

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


@bp.route("/sitemap.xml")
def sitemap():
    """Generate sitemap.xml for SEO."""
    pages = []
    # Add static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            # Exclude API endpoints and outputs
            if not rule.rule.startswith("/api/") and not rule.rule.startswith("/outputs/"):
                pages.append({
                    "loc": url_for(rule.endpoint, _external=True),
                    "lastmod": datetime.now().strftime("%Y-%m-%d"),
                    "changefreq": "weekly",
                    "priority": "1.0" if rule.rule == "/" else "0.8"
                })

    sitemap_xml = render_template("sitemap.xml", pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@bp.route("/robots.txt")
def robots():
    """Generate robots.txt for search engines."""
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /outputs/

Sitemap: {url_for('pages.sitemap', _external=True)}
"""
    response = make_response(robots_txt)
    response.headers["Content-Type"] = "text/plain"
    return response
