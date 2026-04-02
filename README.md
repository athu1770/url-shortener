# snip. — URL Shortener

A minimal but complete URL shortener built with Python + Flask.

## Project Structure

```
url_shortener/
├── app.py            ← Flask backend + API
├── requirements.txt
├── urls.json         ← auto-created on first use
└── static/
    └── index.html    ← Frontend UI
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python app.py
```

Then open http://localhost:5000 in your browser.

## API Endpoints

| Method | Route               | Description              |
|--------|---------------------|--------------------------|
| POST   | /api/shorten        | Create a short URL       |
| GET    | /api/urls           | List all short URLs      |
| DELETE | /api/urls/<code>    | Delete a short URL       |
| GET    | /<code>             | Redirect to original URL |

### POST /api/shorten

```json
{
  "long_url": "https://example.com/very/long/path",
  "custom_code": "mylink"   // optional
}
```

## Features

- Random 6-char alphanumeric short codes
- Optional custom aliases
- Click tracking
- JSON file storage (no database needed)
- Clean dark-mode web UI

## Next Steps (Ideas to Extend)

- [ ] Swap JSON storage for SQLite / PostgreSQL
- [ ] Add expiration dates for links
- [ ] Add QR code generation
- [ ] Password-protect links
- [ ] Analytics dashboard with charts
- [ ] Deploy to Railway / Render / Fly.io
