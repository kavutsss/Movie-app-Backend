# Movie App Backend API

Django REST Framework backend for a movie social application. The project is organized into independent apps for accounts, posts, clubs, and watchlists.

> **Current branch note:** `dev` currently contains the functional posts, clubs, and watchlist implementations. The `accounts/` implementation is incomplete on this branch, although the rest of the project references `accounts.User`. Authentication-related endpoints should be treated as pending until the accounts work is merged.

## Contents

- [Features](#features)
- [Technology](#technology)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the API](#running-the-api)
- [Authentication](#authentication)
- [API conventions](#api-conventions)
- [Posts API](#posts-api)
- [Clubs API](#clubs-api)
- [Watchlist API](#watchlist-api)
- [Data models](#data-models)
- [Testing](#testing)
- [Docker](#docker)
- [Common errors](#common-errors)

## Features

- Movie posts with optional one-to-five-star ratings
- Nested comments on posts
- Like and unlike actions
- Clubs with creator ownership and membership
- Private per-user watchlists
- JWT authentication configuration
- SQLite for local development
- PostgreSQL support through Docker Compose

## Technology

- Python 3.12 recommended
- Django 5.0
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite or PostgreSQL

Dependencies are listed in `requirements.txt`.

## Project structure

```text
.
├── accounts/             Users, authentication, profiles, and follows
├── posts/                Posts, comments, likes, and post routes
├── clubs/                Clubs, membership, and club routes
├── watchlist/            Private watchlists and watchlist routes
├── config/               Settings and root URL configuration
├── manage.py              Django management commands
├── db.sqlite3             Local database, ignored by Git
├── Dockerfile             Container image definition
├── docker-compose.yml     API and PostgreSQL services
├── requirements.txt       Python dependencies
└── schema.dbml            Database relationship diagram
```

## Installation

### Local environment

Create a virtual environment and install dependencies:

```bash
python3 -m venv movie-app
source movie-app/bin/activate
python -m pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver 127.0.0.1:8000
```

Base URL:

```text
http://127.0.0.1:8000
```

## API Documentation

The project exposes interactive OpenAPI documentation through `drf-spectacular`. To open the documentation locally:

1. Install the backend dependencies:

  ```bash
  python -m pip install -r requirements.txt
  ```

2. Apply the database migrations:

  ```bash
  python manage.py migrate
  ```

3. Start the Django development server:

  ```bash
  python manage.py runserver 127.0.0.1:8000
  ```

4. Open the Swagger UI in a browser:

  [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

Swagger UI displays the available endpoints, HTTP methods, request parameters, request bodies, response formats, and authorization controls. Expand an endpoint and select **Try it out** to send a request from the documentation page.

| URL | Description |
| --- | --- |
| `/api/schema/` | OpenAPI 3 schema in JSON/YAML format |
| `/api/docs/` | Interactive Swagger UI |
| `/api/redoc/` | ReDoc documentation |

The documentation URLs are:

- Swagger UI: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- OpenAPI schema: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- ReDoc: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

### Authorizing requests

Protected endpoints require a JWT access token. First log in through `/api/auth/login/` and copy the `access` token from the response. In Swagger UI:

1. Select **Authorize**.
2. Enter `Bearer ACCESS_TOKEN`, replacing `ACCESS_TOKEN` with your token.
3. Select **Authorize**, then close the dialog.
4. Use **Try it out** on a protected endpoint.

The access token is configured to expire after one day. The Swagger interface documents the API available from the running backend; it does not replace authentication or create test data automatically.

The repository's `movie-app/` directory is ignored by Git and is intended for local development only.

## Configuration

Settings are read from environment variables in `config/settings.py`.

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development fallback | Django signing key. Set a private value in deployment. |
| `DJANGO_DEBUG` | `1` | Debug mode. Set to `0` outside local development. |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed host names. |
| `DB_ENGINE` | SQLite | Set to `postgresql` to use PostgreSQL. |
| `DB_NAME` | `moviedb` | PostgreSQL database name. |
| `DB_USER` | `postgres` | PostgreSQL username. |
| `DB_PASSWORD` | `postgres` | PostgreSQL password. |
| `DB_HOST` | `db` | PostgreSQL host. Docker uses the service name `db`. |
| `DB_PORT` | `5432` | PostgreSQL port. |

Without `DB_ENGINE=postgresql`, the API uses `db.sqlite3` in the project root. SQLite database files are ignored by Git and must not be committed.

The current settings allow all CORS origins. Restrict `CORS_ALLOW_ALL_ORIGINS` before production use.

## Running the API

Health and API index routes are defined in `config/urls.py`:

```text
GET /
GET /api/
```

A healthy response has this shape:

```json
{
  "status": "ok",
  "message": "Movie app API is running.",
  "endpoints": {
    "auth": "/api/auth/",
    "users": "/api/users/",
    "posts": "/api/posts/",
    "clubs": "/api/clubs/",
    "watchlist": "/api/watchlist/"
  }
}
```

## Authentication

The settings configure Simple JWT as the default authentication class:

```http
Authorization: Bearer ACCESS_TOKEN
```

The intended authentication routes are:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Register a user |
| `POST` | `/api/auth/login/` | Obtain access and refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Obtain a new access token |
| `POST` | `/api/auth/logout/` | End the client session |

These routes depend on the accounts implementation. On the current `dev` branch, `accounts/models.py`, serializers, views, and URL modules are incomplete, so authentication must be restored before these endpoints can run.

## API conventions

- All API routes use the `/api/` prefix.
- JSON requests should include `Content-Type: application/json`.
- Protected requests require `Authorization: Bearer ACCESS_TOKEN`.
- IDs shown as `<id>` or `<pk>` are integer database IDs.
- Successful creation normally returns `201 Created`.
- Successful deletion normally returns `204 No Content`.
- Invalid input returns `400 Bad Request`.
- Missing credentials returns `401 Unauthorized`.
- Authenticated users without ownership permission receive `403 Forbidden`.
- Missing resources return `404 Not Found`.

The global REST framework permission is `IsAuthenticatedOrReadOnly`. The view-level permissions for the APIs below are authoritative.

## Posts API

Posts are ordered newest first. A post belongs to its authenticated creator and can contain comments and likes.

### Endpoints

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/api/posts/` | Public | List posts |
| `POST` | `/api/posts/` | Required | Create a post |
| `GET` | `/api/posts/<id>/` | Public | Retrieve one post |
| `DELETE` | `/api/posts/<id>/` | Post owner | Delete a post |
| `POST` | `/api/posts/<id>/like/` | Required | Like a post |
| `DELETE` | `/api/posts/<id>/like/` | Required | Remove your like |
| `GET` | `/api/posts/<id>/comments/` | Public by default | List comments |
| `POST` | `/api/posts/<id>/comments/` | Required by default | Add a comment |
| `DELETE` | `/api/comments/<id>/` | Comment owner | Delete a comment |

### Create a post

Required fields are `movie_id`, `movie_title`, and `body`. `stars` is optional and must be between 1 and 5 when supplied.

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{
    "movie_id": 550,
    "movie_title": "Fight Club",
    "body": "Worth watching",
    "stars": 5
  }'
```

The server sets `user`, `created_at`, and `updated_at`. These fields cannot be supplied by the client.

### Post response

```json
{
  "id": 1,
  "user": "Ava",
  "movie_id": 550,
  "movie_title": "Fight Club",
  "body": "Worth watching",
  "stars": 5,
  "like_count": 2,
  "comments": [],
  "created_at": "2026-08-27T12:00:00Z",
  "updated_at": "2026-08-27T12:00:00Z"
}
```

### Like a post

```bash
curl -X POST http://127.0.0.1:8000/api/posts/1/like/ \
  -H 'Authorization: Bearer ACCESS_TOKEN'
```

Response:

```json
{
  "liked": true,
  "like_count": 3
}
```

The delete action returns `liked: false` and the updated `like_count`. Adding the same user more than once does not create duplicate many-to-many rows.

### Add a comment

```bash
curl -X POST http://127.0.0.1:8000/api/posts/1/comments/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{"body":"I agree with this review."}'
```

The server sets the comment's `post`, `user`, and `created_at` fields.

## Clubs API

Clubs are ordered alphabetically by name. The user who creates a club becomes its first member.

### Endpoints

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/api/clubs/` | Public by default | List clubs |
| `POST` | `/api/clubs/` | Required by default | Create a club |
| `GET` | `/api/clubs/<id>/` | Public by default | Retrieve a club |
| `DELETE` | `/api/clubs/<id>/` | Club creator | Delete a club |
| `POST` | `/api/clubs/<id>/join/` | Required | Join a club |
| `DELETE` | `/api/clubs/<id>/join/` | Required | Leave a club |

### Create a club

Accepted fields are `name`, `description`, and `genre`.

```bash
curl -X POST http://127.0.0.1:8000/api/clubs/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{
    "name": "Science Fiction Fans",
    "description": "Discuss science fiction movies",
    "genre": "Science Fiction"
  }'
```

The response includes read-only `id`, `created_by`, `member_count`, and `created_at` fields.

### Join or leave a club

```bash
curl -X POST http://127.0.0.1:8000/api/clubs/1/join/ \
  -H 'Authorization: Bearer ACCESS_TOKEN'

curl -X DELETE http://127.0.0.1:8000/api/clubs/1/join/ \
  -H 'Authorization: Bearer ACCESS_TOKEN'
```

Joining an existing membership is idempotent. A database constraint prevents duplicate memberships for the same user and club.

## Watchlist API

A watchlist is private to the authenticated user. The API filters every list, create, and delete operation by the current user.

### Endpoints

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/api/watchlist/` | Required | List your watchlist |
| `POST` | `/api/watchlist/` | Required | Add a movie |
| `DELETE` | `/api/watchlist/<id>/` | Required | Remove one of your movies |

Watchlist entries are ordered newest first. Required fields are `movie_id` and `movie_title`; `poster_path` is optional.

```bash
curl -X POST http://127.0.0.1:8000/api/watchlist/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{
    "movie_id": 550,
    "movie_title": "Fight Club",
    "poster_path": "/poster.jpg"
  }'
```

A database constraint prevents the same user from adding the same `movie_id` more than once.

## Data models

### Post

| Field | Type | Notes |
| --- | --- | --- |
| `user` | Foreign key | Authenticated creator |
| `movie_id` | Positive integer | External movie identifier |
| `movie_title` | String | Maximum 255 characters |
| `body` | Text | Review or post content |
| `stars` | Small integer | Optional, from 1 to 5 |
| `likes` | Many-to-many users | Users who liked the post |
| `created_at` | Date/time | Set automatically |
| `updated_at` | Date/time | Updated automatically |

### Comment

| Field | Type | Notes |
| --- | --- | --- |
| `post` | Foreign key | Related post |
| `user` | Foreign key | Comment author |
| `body` | Text | Comment content |
| `created_at` | Date/time | Set automatically |

### Club and ClubMember

`Club` stores `name`, `description`, `genre`, `created_by`, and `created_at`. `ClubMember` connects users to clubs and stores `joined_at`. The `(club, user)` pair is unique.

### Watchlist

`Watchlist` stores `user`, `movie_id`, `movie_title`, `poster_path`, and `created_at`. The `(user, movie_id)` pair is unique.

## Database migrations

Create migrations after changing models:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

The Django admin is available at `/admin/` when enabled and the server is running.

## Testing

Run Django's system checks:

```bash
python manage.py check
```

Run all tests:

```bash
python manage.py test
```

On the current branch, tests and checks cannot complete until the `accounts.User` model and related accounts modules are restored.

## Docker

The Compose configuration starts:

- `db`: PostgreSQL 16 Alpine
- `api`: Django API on port `8000`

Start both services:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

Stop services and delete PostgreSQL data:

```bash
docker compose down -v
```

The API container runs migrations before starting the development server. Docker Compose supplies PostgreSQL settings through `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_HOST`.

## Common errors

### `AUTH_USER_MODEL refers to model 'accounts.User'`

The accounts app does not currently define the configured custom user model. Restore the accounts implementation and migrations before running Django.

### `Need to specify how to reconcile divergent branches`

Git found that local and remote branches both contain commits. Specify the intended strategy explicitly:

```bash
git pull --no-rebase origin dev
```

Use a merge when preserving both branch histories is important. Do not use `--ff-only` when the branches have diverged.

### Database or virtual environment files appear in Git

The root `.gitignore` excludes SQLite databases, Python caches, environment files, and the local `movie-app/` virtual environment. Check the rule with:

```bash
git check-ignore -v db.sqlite3 movie-app/bin/python
```

## Production checklist

Before deployment:

- Set a strong private `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=0`.
- Replace `ALLOWED_HOSTS=*` with explicit hosts.
- Restrict CORS origins.
- Use non-default PostgreSQL credentials.
- Run migrations during deployment.
- Do not commit `db.sqlite3`, `.env`, or virtual-environment files.
- Run `python manage.py check` and `python manage.py test` in CI.
