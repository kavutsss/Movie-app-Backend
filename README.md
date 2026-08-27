# Movie App Backend

Django REST API for a movie social application. The API supports authentication, user profiles, follows, movie posts, comments, likes, clubs, and personal watchlists.

## Team File Ownership

### Member 1: Accounts and Authentication

**Files owned:**

```text
accounts/models.py
accounts/serializers.py
accounts/views.py
accounts/urls_auth.py
accounts/urls_users.py
accounts/tests.py
accounts/migrations/
```

**Main code responsibilities:**


**Important code areas:**

```python
# accounts/models.py
class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    following = models.ManyToManyField('self', symmetrical=False, blank=True)
```

**Endpoints:**

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
POST /api/auth/logout/
GET  /api/users/
GET  /api/users/<id>/
PUT  /api/users/<id>/
POST /api/users/<id>/follow/
DELETE /api/users/<id>/follow/
```

**Example registration request:**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"strong-pass-123"}'
```

### Member 2: Posts, Comments, and Likes

**Files owned:**

```text
posts/models.py
posts/serializers.py
posts/views.py
posts/urls.py
posts/tests.py
posts/migrations/
```

**Main code responsibilities:**


**Main models:**

```python
# posts/models.py
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie_id = models.PositiveIntegerField()
    movie_title = models.CharField(max_length=255)
    body = models.TextField()
    stars = models.PositiveSmallIntegerField(null=True, blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
```

**Endpoints:**

```text
GET    /api/posts/
POST   /api/posts/
GET    /api/posts/<id>/
DELETE /api/posts/<id>/
POST   /api/posts/<id>/like/
DELETE /api/posts/<id>/like/
GET    /api/posts/<id>/comments/
POST   /api/posts/<id>/comments/
DELETE /api/comments/<id>/
```

**Example authenticated post request:**

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"movie_id":550,"movie_title":"Fight Club","body":"Worth watching","stars":5}'
```

### Member 3: Clubs and Watchlist

Member 3 owns two smaller Django apps.

**Club files:**

```text
clubs/models.py
clubs/serializers.py
clubs/views.py
clubs/urls.py
clubs/tests.py
clubs/migrations/
```

**Watchlist files:**

```text
watchlist/models.py
watchlist/serializers.py
watchlist/views.py
watchlist/urls.py
watchlist/tests.py
watchlist/migrations/
```

**Main code responsibilities:**


**Main models:**

```python
# clubs/models.py
class Club(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class ClubMember(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

```python
# watchlist/models.py
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie_id = models.PositiveIntegerField()
    movie_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True)
```

**Club endpoints:**

```text
GET    /api/clubs/
POST   /api/clubs/
GET    /api/clubs/<id>/
DELETE /api/clubs/<id>/
POST   /api/clubs/<id>/join/
DELETE /api/clubs/<id>/join/
```

**Watchlist endpoints:**

```text
GET    /api/watchlist/
POST   /api/watchlist/
DELETE /api/watchlist/<id>/
```

**Example watchlist request:**

```bash
curl -X POST http://127.0.0.1:8000/api/watchlist/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"movie_id":550,"movie_title":"Fight Club","poster_path":"/poster.jpg"}'
```

### Member 4: Integration, Configuration, Testing, and Docker

**Files owned:**

```text
config/settings.py
config/urls.py
config/asgi.py
config/wsgi.py
manage.py
requirements.txt
Dockerfile
docker-compose.yml
schema.dbml
```

**Main code responsibilities:**


**Useful project commands:**

```bash
# Check the project
./movie-app/bin/python manage.py check

# Movie App Backend

A Django REST Framework API for a movie-focused social application. It provides JWT authentication, user profiles and follows, movie posts, comments, likes, clubs, and private watchlists.

## Features

- Email-based custom user model
- JWT access and refresh tokens
- Public user profiles and authenticated profile updates
- Follow and unfollow users
- Create and browse movie posts
- Rate posts from one to five stars
- Comment on posts
- Like and unlike posts
- Create clubs and manage membership
- Maintain a personal watchlist
- SQLite for local development
- PostgreSQL support through Docker and environment variables

## Technology

- Python 3.12 recommended
- Django 5.0, as pinned in `requirements.txt`
- Django REST Framework
- `djangorestframework-simplejwt`
- `django-cors-headers`
- SQLite or PostgreSQL

## Project Structure

```text
.
├── accounts/       Custom user, authentication, profiles, and follows
├── posts/          Posts, comments, likes, serializers, and endpoints
├── clubs/          Clubs and club membership
├── watchlist/      User watchlists
├── config/         Django settings, URL configuration, ASGI, and WSGI
├── manage.py       Django command-line entry point
├── db.sqlite3      Local SQLite database
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── schema.dbml     Database relationship diagram
```

## Installation

### Local setup

Create and activate a virtual environment. The repository currently includes a virtual environment in `movie-app/`, but a new environment can also be used.

```bash
python3 -m venv movie-app
source movie-app/bin/activate
python -m pip install -r requirements.txt
```

Apply migrations and check the project:

```bash
python manage.py migrate
python manage.py check
```

Start the development server:

```bash
python manage.py runserver 127.0.0.1:8000
```

The API is available at `http://127.0.0.1:8000/`.

### Docker setup

Docker Compose starts the API and a PostgreSQL 16 database. The API container automatically runs migrations before starting Django.

```bash
docker compose up --build
```

Stop the services:

```bash
docker compose down
```

To remove the PostgreSQL volume as well, which deletes its stored data:

```bash
docker compose down -v
```

## Configuration

The application reads these environment variables from `config/settings.py`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development fallback | Django signing key; set a private value outside local development |
| `DJANGO_DEBUG` | `1` | Debug mode; use `0` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DB_ENGINE` | SQLite | Set to `postgresql` to use PostgreSQL |
| `DB_NAME` | `moviedb` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | `postgres` | PostgreSQL password |
| `DB_HOST` | `db` | PostgreSQL host; Docker Compose uses `db` |
| `DB_PORT` | `5432` | PostgreSQL port |

When `DB_ENGINE` is not `postgresql`, the project uses `db.sqlite3` in the repository root. CORS is currently open to all origins through `CORS_ALLOW_ALL_ORIGINS = True`; restrict this before production deployment.

## Authentication

Authentication uses JSON Web Tokens. Login returns an access token and a refresh token. Send the access token with protected requests:

```http
Authorization: Bearer ACCESS_TOKEN
```

Access tokens are configured to expire after one day. The logout endpoint verifies that the caller is authenticated but does not blacklist tokens; clients should discard their tokens after logout.

## API Overview

All API routes use the `/api/` prefix. The root endpoints return a health response and links to the main API areas:

```text
GET /
GET /api/
GET /api/auth/
```

The normal REST framework default is `IsAuthenticatedOrReadOnly`: unauthenticated users can read public resources, while create, update, delete, like, follow, join, and watchlist operations require authentication unless an endpoint states otherwise.

## Authentication and Users

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `GET` | `/api/auth/` | Lists authentication links | Public |
| `POST` | `/api/auth/register/` | Registers a user | Public |
| `POST` | `/api/auth/login/` | Returns JWT access and refresh tokens | Public |
| `POST` | `/api/auth/token/refresh/` | Refreshes an access token | Public with refresh token |
| `POST` | `/api/auth/logout/` | Confirms logout request | Authenticated |
| `GET` | `/api/users/` | Lists users | Public |
| `GET` | `/api/users/<id>/` | Retrieves a user profile | Public |
| `PUT` or `PATCH` | `/api/users/<id>/` | Updates your own profile | Authenticated owner |
| `POST` | `/api/users/<id>/follow/` | Follows another user | Authenticated |
| `DELETE` | `/api/users/<id>/follow/` | Unfollows a user | Authenticated |

Registration requires `name`, `email`, and a password of at least eight characters. Email addresses are unique, and email is the login field.

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test User","email":"test@example.com","password":"strong-pass-123"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"strong-pass-123"}'
```

The response contains `access` and `refresh` fields. Use the value of `access` for protected endpoints.

## Posts, Comments, and Likes

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/posts/` | Lists posts, newest first |
| `POST` | `/api/posts/` | Creates a post for the authenticated user |
| `GET` | `/api/posts/<id>/` | Retrieves a post with comments and like count |
| `DELETE` | `/api/posts/<id>/` | Deletes a post; owner only |
| `POST` | `/api/posts/<id>/like/` | Likes a post |
| `DELETE` | `/api/posts/<id>/like/` | Removes your like |
| `GET` | `/api/posts/<id>/comments/` | Lists comments for a post |
| `POST` | `/api/posts/<id>/comments/` | Adds a comment |
| `DELETE` | `/api/comments/<id>/` | Deletes a comment; owner only |

Create a post with `movie_id`, `movie_title`, and `body`. `stars` is optional, but when supplied it must be between 1 and 5.

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{"movie_id":550,"movie_title":"Fight Club","body":"Worth watching","stars":5}'
```

The API assigns the post owner and timestamps. Post responses include `like_count` and a nested read-only `comments` list. Posts and comments are ordered newest first and oldest first respectively.

## Clubs

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/clubs/` | Lists clubs alphabetically |
| `POST` | `/api/clubs/` | Creates a club and adds the creator as a member |
| `GET` | `/api/clubs/<id>/` | Retrieves a club |
| `DELETE` | `/api/clubs/<id>/` | Deletes a club; creator only |
| `POST` | `/api/clubs/<id>/join/` | Joins a club; repeated joins are idempotent |
| `DELETE` | `/api/clubs/<id>/join/` | Leaves a club |

Club creation accepts `name`, `description`, and `genre`. The response includes the creator and `member_count`. A database constraint prevents duplicate membership for the same user and club.

```bash
curl -X POST http://127.0.0.1:8000/api/clubs/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{"name":"Science Fiction Fans","description":"Discuss science fiction movies","genre":"Science Fiction"}'
```

## Watchlist

Each authenticated user can view and modify only their own watchlist.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/watchlist/` | Lists your watchlist, newest first |
| `POST` | `/api/watchlist/` | Adds a movie to your watchlist |
| `DELETE` | `/api/watchlist/<id>/` | Removes one of your watchlist entries |

The request fields are `movie_id`, `movie_title`, and optional `poster_path`. A user cannot add the same `movie_id` more than once.

```bash
curl -X POST http://127.0.0.1:8000/api/watchlist/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -d '{"movie_id":550,"movie_title":"Fight Club","poster_path":"/poster.jpg"}'
```

## Response and Error Behavior

The API uses standard HTTP status codes:

- `200 OK`: Successful read or action
- `201 Created`: Successful registration or creation
- `204 No Content`: Successful deletion or removal
- `400 Bad Request`: Invalid input, such as an invalid star rating or following yourself
- `401 Unauthorized`: Missing or invalid JWT credentials
- `403 Forbidden`: Authenticated user lacks ownership permission
- `404 Not Found`: Requested object does not exist

Validation and permission errors are returned as JSON. For example, only the owner can update their profile, delete their posts or comments, or delete a club they created.

## Database and Migrations

After changing a model, create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an administrator for the Django admin site with:

```bash
python manage.py createsuperuser
```

The admin site is available at `/admin/` when the development server is running.

## Testing and Quality Checks

Run the complete test suite and Django system checks:

```bash
python manage.py test
python manage.py check
```

With the repository virtual environment, use `./movie-app/bin/python` instead of `python`:

```bash
./movie-app/bin/python manage.py test
./movie-app/bin/python manage.py check
```

## Production Notes

Before deploying, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=0`, configure explicit `DJANGO_ALLOWED_HOSTS`, restrict CORS origins, and use PostgreSQL or another production database. Do not use the development database credentials from `docker-compose.yml` in a public environment.

## License

No license file is currently included in this repository.
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, pk):
    club = generics.get_object_or_404(Club, pk=pk)
    membership, _ = ClubMember.objects.get_or_create(club=club, user=request.user)
    return Response(ClubMemberSerializer(membership).data, status=201)

urlpatterns = [
  path('clubs/', ClubListCreateView.as_view(), name='club-list'),
  path('clubs/<int:pk>/', ClubDetailView.as_view(), name='club-detail'),
  path('clubs/<int:pk>/join/', ClubMembershipView.as_view(), name='club-membership'),
]
```

#### `watchlist/models.py` and `watchlist/views.py`

```python
class Watchlist(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
  movie_id = models.PositiveIntegerField()
  movie_title = models.CharField(max_length=255)
  poster_path = models.CharField(max_length=255, blank=True)

class WatchlistListCreateView(generics.ListCreateAPIView):
  serializer_class = WatchlistSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return Watchlist.objects.filter(user=self.request.user)

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)
```

#### `watchlist/serializers.py` and `watchlist/urls.py`

```python
class WatchlistSerializer(serializers.ModelSerializer):
  class Meta:
    model = Watchlist
    fields = ['id', 'movie_id', 'movie_title', 'poster_path', 'created_at']
    read_only_fields = ['id', 'created_at']

urlpatterns = [
  path('watchlist/', WatchlistListCreateView.as_view(), name='watchlist-list'),
  path('watchlist/<int:pk>/', WatchlistDetailView.as_view(), name='watchlist-detail'),
]
```

### Member 4: Configuration and Deployment

#### `config/urls.py`

```python
urlpatterns = [
  path('', api_root, name='api-health'),
  path('api/', api_root, name='api-root'),
  path('api/auth/', include('accounts.urls_auth')),
  path('api/users/', include('accounts.urls_users')),
  path('api/', include('posts.urls')),
  path('api/', include('clubs.urls')),
  path('api/', include('watchlist.urls')),
]
```

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### `requirements.txt`

```text
Django==5.0
djangorestframework
djangorestframework-simplejwt
django-cors-headers
psycopg2-binary
python-dotenv
```

Member 4 also maintains `config/settings.py`, `config/asgi.py`, `config/wsgi.py`, `docker-compose.yml`, `schema.dbml`, `manage.py`, and the generated migration files. These configure the database, connect the applications, support deployment, and document the schema.

### Member 2: Posts

#### `posts/models.py`

```python
class Post(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
  movie_id = models.PositiveIntegerField()
  movie_title = models.CharField(max_length=255)
  body = models.TextField()
  stars = models.PositiveSmallIntegerField(null=True, blank=True)
  likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')

class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
  body = models.TextField()
```

#### `posts/serializers.py`

```python
class PostSerializer(serializers.ModelSerializer):
  user = serializers.StringRelatedField(read_only=True)
  like_count = serializers.IntegerField(source='likes.count', read_only=True)
  comments = CommentSerializer(many=True, read_only=True)

  class Meta:
    model = Post
    fields = ['id', 'user', 'movie_id', 'movie_title', 'body', 'stars', 'like_count', 'comments', 'created_at', 'updated_at']

  def validate_stars(self, value):
    if value < 1 or value > 5:
      raise serializers.ValidationError('Stars must be between 1 and 5.')
    return value
```

#### `posts/views.py` and `posts/urls.py`

```python
class PostListCreateView(generics.ListCreateAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

class LikeView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, pk):
    post = generics.get_object_or_404(Post, pk=pk)
    post.likes.add(request.user)
    return Response({'liked': True, 'like_count': post.likes.count()})

urlpatterns = [
  path('posts/', PostListCreateView.as_view(), name='post-list'),
  path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
  path('posts/<int:pk>/like/', LikeView.as_view(), name='post-like'),
  path('posts/<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
  path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]
```
