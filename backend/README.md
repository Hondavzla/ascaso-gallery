# Ascaso Gallery — Backend

Flask + SQLAlchemy JSON API.

## First-run setup (dev)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env    # fill in CLOUDINARY_URL + any secrets
flask db upgrade
flask seed
flask create-admin      # interactive
flask run               # http://localhost:5000
```

## Tests

```bash
pytest
```

## Deploy

Auto-deploys to Render via `render.yaml` on push to `main`.
