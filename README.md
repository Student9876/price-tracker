# Price Tracker — Backend

Short guide to set up and run the backend.

## Prerequisites
- Python 3.10+
- A database (e.g., PostgreSQL) configured via environment variable
- Git (optional)

## Quick setup
1. Open a terminal and go to the backend folder:
   ```sh
   cd backend
   ```
2. Create & activate a virtual environment and install dependencies:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # or
   source .venv/bin/activate   # macOS / Linux

   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Configure environment:
   - Create or update `.env` in the `backend` folder and set `DATABASE_URL`, `SECRET_KEY`, and other settings used by `core.config`.
   - Confirm `db/session.py` uses the correct `DATABASE_URL`.

## Run the API
From the `backend` directory with the venv activated:
```sh
uvicorn main:app --reload
```
The entrypoint is `backend/main.py`. Database tables are created automatically by `Base.metadata.create_all(bind=engine)` on startup.

## Optional: Scheduler
A periodic price-check job may exist (e.g., `scheduler.py`). Run it as a separate process or service if you need background polling.

## Key files / modules
- `backend/main.py` — FastAPI app and route definitions
- `backend/scraper.py` — scraper coordinator (`scrape_url`)
- `backend/scrapers/` — site-specific scrapers (e.g., `amazon.py`)
- `backend/crud_operations.py` — DB helpers / CRUD
- `backend/models/` — SQLAlchemy models (Product, PriceHistory, User, etc.)
- `backend/schemas.py` — Pydantic request/response schemas
- `backend/api/deps.py` — auth dependencies (e.g., `get_current_user`)
- `backend/core/security.py` — auth helpers (hashing, token creation)
- `backend/db/session.py` and `backend/db/base.py` — DB setup

## Routes (summary)
- POST /auth/register
  - Request: `schemas.UserCreate`
  - Response: `schemas.User`
  - Create a new user.

- POST /auth/login
  - Request: OAuth2 password form (username/email + password)
  - Response: `schemas.Token`
  - Returns a JWT on successful authentication.

- POST /scrape
  - Request: `schemas.ScrapeRequest` (list or single URL)
  - Response: list of `schemas.ProductDetails` or `schemas.ErrorResponse`
  - Uses `scraper.scrape_url` to fetch product/listing info.

- GET /track
  - Protected (Bearer token)
  - Response: list of `schemas.TrackedProductResponse`
  - Returns products tracked by the authenticated user.

- POST /track
  - Protected
  - Request: `schemas.ScrapeRequest` (single URL expected)
  - Scrapes, creates product if needed, and links it to the user.

## Troubleshooting
- "Fatal error in launcher: Unable to create process" when running `uvicorn`:
  - Ensure you run `uvicorn` from the `backend` folder with the correct virtual environment activated.
  - Example on Windows:
    ```sh
    cd backend
    .venv\Scripts\activate
    uvicorn main:app --reload
    ```
- SQLAlchemy mapper errors (e.g., missing `PriceHistory`):
  - Ensure model modules are imported before `Base.metadata.create_all(...)` so relationships can be resolved.
  - Example: import `models.product` and `models.price_history` in `main.py` before creating tables.

## Notes
- Keep `requirements.txt` up to date (generate with `pip freeze > requirements.txt` inside the venv).
- Store secrets in `.env` and add `.env` to `.gitignore`.
- Review `scrapers/` and adjust selectors if pages change.

For implementation details, inspect:
- `backend/scraper.py`
- `backend/crud_operations.py`
- `backend/schemas.py`
- `backend/api/deps.py`