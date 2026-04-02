"""
URL Shortener - app.py
A simple Flask-based URL shortener with JSON file storage.
"""

from flask import Flask, request, redirect, jsonify, send_from_directory
import json
import os
import random
import string
from datetime import datetime

app = Flask(__name__, static_folder="static")
DB_FILE = "urls.json"


# ---------- Storage helpers ----------

def load_db() -> dict:
    """Load the URL database from disk."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db: dict) -> None:
    """Persist the URL database to disk."""
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# ---------- Core logic ----------

def generate_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def create_short_url(long_url: str, custom_code: str = None) -> dict:
    """
    Create a shortened URL entry.
    Returns a dict with the short code and metadata.
    Raises ValueError if the custom code is already taken.
    """
    db = load_db()

    # Use custom code or generate a unique one
    if custom_code:
        if custom_code in db:
            raise ValueError(f"Custom code '{custom_code}' is already in use.")
        code = custom_code
    else:
        code = generate_code()
        while code in db:          # Avoid (unlikely) collisions
            code = generate_code()

    entry = {
        "long_url": long_url,
        "created_at": datetime.utcnow().isoformat(),
        "clicks": 0,
    }
    db[code] = entry
    save_db(db)
    return {"code": code, **entry}


def get_url(code: str) -> dict | None:
    """Look up a short code and increment its click counter."""
    db = load_db()
    entry = db.get(code)
    if entry:
        entry["clicks"] += 1
        save_db(db)
    return entry


def list_urls() -> list[dict]:
    """Return all stored URLs as a list."""
    db = load_db()
    return [{"code": code, **data} for code, data in db.items()]


def delete_url(code: str) -> bool:
    """Delete a short URL. Returns True if it existed."""
    db = load_db()
    if code not in db:
        return False
    del db[code]
    save_db(db)
    return True


# ---------- API routes ----------

@app.route("/api/shorten", methods=["POST"])
def shorten():
    """POST /api/shorten  →  { long_url, custom_code? }"""
    body = request.get_json(silent=True) or {}
    long_url = (body.get("long_url") or "").strip()
    custom_code = (body.get("custom_code") or "").strip() or None

    if not long_url:
        return jsonify({"error": "long_url is required"}), 400

    # Basic URL validation
    if not long_url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    try:
        result = create_short_url(long_url, custom_code)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    base = request.host_url.rstrip("/")
    result["short_url"] = f"{base}/{result['code']}"
    return jsonify(result), 201


@app.route("/api/urls", methods=["GET"])
def list_all():
    """GET /api/urls  →  list of all URLs"""
    urls = list_urls()
    base = request.host_url.rstrip("/")
    for u in urls:
        u["short_url"] = f"{base}/{u['code']}"
    return jsonify(urls)


@app.route("/api/urls/<code>", methods=["DELETE"])
def delete(code: str):
    """DELETE /api/urls/<code>"""
    if delete_url(code):
        return jsonify({"message": f"Deleted '{code}'"}), 200
    return jsonify({"error": "Code not found"}), 404


# ---------- Redirect route ----------

@app.route("/<code>")
def redirect_to_url(code: str):
    """Redirect short code → original URL."""
    entry = get_url(code)
    if entry:
        return redirect(entry["long_url"], code=302)
    return jsonify({"error": "Short URL not found"}), 404


# ---------- Serve frontend ----------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
