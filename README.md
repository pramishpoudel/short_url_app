# Vrittech — URL Shortener (Django)

A simple URL shortener web application built with Django. Users can register, log in, create shortened links (base62), set custom aliases and expiration times, manage their short URLs (edit, delete, regenerate), and view basic analytics including click counts and QR codes.

---

##  Features

- User authentication: register, login, logout 
- Create short URLs with automatic Base62 key generation 
- Optional custom alias (alphanumeric) with uniqueness validation 
- Optional expiration time for short URLs  
- Redirects from `/s/<key>/` to the original URL (expires respected) 
- Manage links: list, edit (including changing short key), delete, regenerate key 
- Basic analytics: click count, created and expire timestamps 
- QR code generation (embedded PNG data URI; requires `qrcode[pil]`) 
- Admin integration for inspecting `ShortURL` and `Profile` models 

---

##  Requirements

- Python >= 3.13 (see `pyproject.toml`) — or any version compatible with Django 6
- Poetry (recommended) or pip
- Optional: `qrcode[pil]` for QR code generation

---

##  Setup (development)

Clone the repo and install dependencies:

```bash
git clone <repo-url>
cd Vrittech/Backend
poetry install
```

Create and apply migrations:

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

Create a superuser (optional):

```bash
poetry run python manage.py createsuperuser
```

Run the dev server:

```bash
poetry run python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and sign up / log in.

---

##  Usage

- Create a short URL: Visit `/shorts/create/` (must be authenticated). You can optionally provide a custom alias and an expiration date/time.
- Manage URLs: `/shorts/` lists your short URLs with actions to Edit / Delete / Stats / Regenerate.
- View Stats: `/shorts/<pk>/stats/` shows clicks, created/expire timestamps, and a QR code (if `qrcode` is installed).
- Public redirect: `GET /s/<key>/` will redirect to the original URL (returns 404 if expired).

---

## Routes & Endpoints

Below is a concise list of the main routes used in the project, their HTTP methods, authentication/permission requirements and a short description.

| URL | Django name | Methods | Auth | Description |
|---|---:|---:|---:|---|
| / | `home` | GET | Public | Home / landing page |
| /login/ | `login` | GET, POST | Public | Login page (POST to authenticate) |
| /logout/ | `logout` | GET | Authenticated | Logs out the current user and redirects to login |
| /register/ | `signup` | GET, POST | Public | User registration page |
| /shorts/ | `short_list` | GET | Authenticated | List of the current user's short URLs (clicks, created, expires, actions) |
| /shorts/create/ | `short_create` | GET, POST | Authenticated | Create a new short URL. Fields: `original_url`, optional `custom_key` (alphanumeric), optional `expires_at` |
| /shorts/<int:pk>/edit/ | `short_edit` | GET, POST | Owner only | Edit original URL, change custom alias or expiry (validated uniqueness) |
| /shorts/<int:pk>/delete/ | `short_delete` | GET, POST | Owner only | Confirm and delete a short URL |
| /shorts/<int:pk>/stats/ | `short_stats` | GET | Owner only | View clicks, created/expire timestamps and QR code (if available) |
| /shorts/<int:pk>/regenerate/ | `short_regenerate` | GET, POST | Owner only | Regenerate the short key (old key becomes invalid) |
| /s/<str:key>/ | `short_redirect` | GET | Public | Public redirect: resolves the short key to the original URL (returns 404 if expired or not found) |
| /admin/ | Django admin | GET, POST | Admin | Django admin interface (manage models)

> Note: Named URL patterns (`name=`) appear in the code and templates — use them for reverse lookups in views/templates.

---


##  Implementation notes

- Keys are generated deterministically using Base62 encoding of the model PK when not explicitly provided. Regenerate creates a new unique suffix to avoid collisions.
- Expiration is stored in `ShortURL.expires_at` and enforced in the redirect view.
- QR codes are generated on-demand using the `qrcode` library and embedded as data URIs; no files are stored.

---

##  Environment variables

Set these variables in production (example `.env`):

```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/dbname
ALLOWED_HOSTS=yourdomain.com
 
```

Note: In development with `DEBUG=True`, Django serves static files automatically.

---

##  Tests

Run the Django test suite:

```bash
poetry run python manage.py test
```

---

## 📦 Deployment (GitHub Actions -> Heroku example)

A sample workflow `.github/workflows/deploy.yml` is included. It:

- Installs dependencies with Poetry
- Runs migrations and tests
- Collects static files
- Optionally deploys to Heroku using secrets: `HEROKU_API_KEY`, `HEROKU_APP`, `HEROKU_EMAIL`

Make sure to add those secrets to your GitHub repository if you want the deployment step to run automatically on `push` to `main`.

---

##  Optional improvements

- Add per-click logging (IP, referer, timestamp) for advanced analytics
- Preserve previous keys on regeneration with an alias/history table
- Add client-side date/time pickers for nicer expiry input
- Add Dockerfile and Docker Compose for reproducible deployments

---

 