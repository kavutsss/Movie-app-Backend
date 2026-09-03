# Quick Integration Guide - Backend & Frontend

This guide helps developers quickly integrate the backend API with the frontend React application.

## Quick Start

### Backend Setup (Local Development)

```bash
# 1. Clone and navigate to backend
cd Movie-app-Backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy from .env.example)
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup (Local Development)

```bash
# 1. Navigate to frontend
cd Movie-app-Frontend

# 2. Install dependencies
npm install

# 3. Create .env file (copy from .env.example)
cp .env.example .env

# 4. Update .env with backend URL
# VITE_BACKEND_API_URL=http://localhost:8000/api

# 5. Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173` (or as shown in terminal)

---

## Using the Backend API in Frontend

### 1. Import the API Client

```javascript
import backendApi from '@/services/backendApi';
```

### 2. Common API Operations

#### Authentication

```javascript
// Login
const response = await backendApi.auth.login(email, password);
backendApi.setToken(response.access);  // Store token
localStorage.setItem('refresh_token', response.refresh);

// Signup
const newUser = await backendApi.auth.signup({
  username: 'john_doe',
  email: 'john@example.com',
  password: 'secure_password'
});

// Logout
await backendApi.auth.logout();
backendApi.clearToken();
```

#### User Operations

```javascript
// Get user profile
const profile = await backendApi.users.getProfile(userId);

// Update profile
const updated = await backendApi.users.updateProfile(userId, {
  bio: 'Movie enthusiast',
  avatar: 'profile_pic_url'
});

// Follow user
await backendApi.users.follow(userId);

// Get followers
const followers = await backendApi.users.getFollowers(userId);
```

#### Posts

```javascript
// Get all posts
const posts = await backendApi.posts.list({ page: 1 });

// Create post
const newPost = await backendApi.posts.create({
  title: 'Great Movie Review',
  content: 'This movie was amazing!',
  rating: 5,
  movie_id: 550  // TMDB movie ID
});

// Like a post
await backendApi.posts.like(postId);

// Unlike a post
await backendApi.posts.unlike(postId);

// Add comment
await backendApi.comments.create(postId, {
  content: 'I totally agree!'
});

// Delete comment
await backendApi.comments.delete(postId, commentId);
```

#### Clubs

```javascript
// Get clubs
const clubs = await backendApi.clubs.list();

// Create club
const club = await backendApi.clubs.create({
  name: 'Action Movie Fans',
  description: 'For lovers of action films',
  image_url: 'club_image_url'
});

// Join club
await backendApi.clubs.join(clubId);

// Get club members
const members = await backendApi.clubs.getMembers(clubId);

// Leave club
await backendApi.clubs.leave(clubId);
```

#### Watchlist

```javascript
// Get user's watchlist
const watchlist = await backendApi.watchlist.list();

// Add movie to watchlist
await backendApi.watchlist.add({
  movie_id: 550,  // TMDB movie ID
  title: 'Fight Club'
});

// Mark movie as watched
await backendApi.watchlist.markWatched(watchlistItemId);

// Remove from watchlist
await backendApi.watchlist.remove(watchlistItemId);
```

---

## API Endpoints Reference

### Authentication
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/register/` - Create new user account
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/token/refresh/` - Refresh access token

### Users
- `GET /api/users/<id>/` - Get user profile
- `PUT /api/users/<id>/` - Update profile
- `GET /api/users/<id>/followers/` - Get user's followers
- `GET /api/users/<id>/following/` - Get users that user follows
- `POST /api/users/<id>/follow/` - Follow user
- `POST /api/users/<id>/unfollow/` - Unfollow user

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create new post
- `GET /api/posts/<id>/` - Get post details
- `PUT /api/posts/<id>/` - Update post
- `DELETE /api/posts/<id>/` - Delete post
- `POST /api/posts/<id>/like/` - Like post
- `POST /api/posts/<id>/unlike/` - Unlike post
- `GET /api/posts/<id>/comments/` - Get post comments
- `POST /api/posts/<id>/comments/` - Add comment
- `DELETE /api/posts/<id>/comments/<comment_id>/` - Delete comment

### Clubs
- `GET /api/clubs/` - List all clubs
- `POST /api/clubs/` - Create new club
- `GET /api/clubs/<id>/` - Get club details
- `PUT /api/clubs/<id>/` - Update club
- `DELETE /api/clubs/<id>/` - Delete club
- `POST /api/clubs/<id>/join/` - Join club
- `POST /api/clubs/<id>/leave/` - Leave club
- `GET /api/clubs/<id>/members/` - Get club members

### Watchlist
- `GET /api/watchlist/` - Get user's watchlist
- `POST /api/watchlist/` - Add movie to watchlist
- `DELETE /api/watchlist/<id>/` - Remove from watchlist
- `PATCH /api/watchlist/<id>/watched/` - Mark as watched

---

## Response Handling

All API responses include:
- Status code (2xx for success, 4xx/5xx for errors)
- JSON response body
- Headers including CORS allowance

### Successful Response (200)
```javascript
const response = await backendApi.posts.list();
// response = {
//   count: 10,
//   next: '/api/posts/?page=2',
//   previous: null,
//   results: [...]
// }
```

### Error Response (5xx)
```javascript
try {
  await backendApi.posts.create({ title: 'Test' });
} catch (error) {
  console.error('Failed to create post:', error.message);
}
```

---

## Token Management

The API client automatically:
- Stores access token in localStorage
- Sends token with every authenticated request
- Handles 401 (Unauthorized) errors
- Redirects to login if token is invalid

### Manual Token Management

```javascript
// Set token after login
backendApi.setToken(accessToken);

// Clear token on logout
backendApi.clearToken();

// Get current token (for advanced usage)
const token = localStorage.getItem('access_token');
```

---

## Debugging

### Enable Logging

```javascript
// In browser console
localStorage.setItem('debug', 'true');

// Or set in development
if (import.meta.env.DEV) {
  window.DEBUG_API = true;
}
```

### Common Issues

**CORS Error**
- Backend URL in .env must match exactly
- Backend CORS_ALLOWED_ORIGINS must include frontend URL
- Check browser console for specific error

**401 Unauthorized**
- Token may have expired
- Refresh token or re-login
- Check localStorage for access_token

**Network Error**
- Backend server may not be running
- Check backend URL in .env
- Verify backend is accessible: `curl http://localhost:8000/api/`

### Testing in Browser Console

```javascript
// Direct API call test
fetch('http://localhost:8000/api/', {
  headers: { 'Accept': 'application/json' }
})
.then(r => r.json())
.then(data => console.log(data));

// Using API client
backendApi.posts.list()
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

---

## Development Workflow

### 1. Backend Development
```bash
cd Movie-app-Backend
python manage.py runserver
# API available at http://localhost:8000/api
```

### 2. Frontend Development
```bash
cd Movie-app-Frontend
npm run dev
# App available at http://localhost:5173
```

### 3. Monitor Requests
- Open browser DevTools (F12)
- Go to Network tab
- Interact with app and watch API calls
- Check Console tab for errors

### 4. Test New Endpoints

In React component:
```javascript
import { useEffect, useState } from 'react';
import backendApi from '@/services/backendApi';

export function TestComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    backendApi.posts.list()
      .then(setData)
      .catch(console.error);
  }, []);

  return <div>{JSON.stringify(data)}</div>;
}
```

---

## Production Considerations

### Environment Variables
For Render deployment:
- Backend: Set `VITE_BACKEND_API_URL=https://movie-app-api.onrender.com/api`
- Backend: Set `DJANGO_ALLOWED_HOSTS` to include frontend URL

### CORS Configuration
The backend is configured to allow:
- Frontend from Render
- Local development URLs
- Specific CORS origins from environment variable

### Authentication
- Uses JWT tokens
- Tokens stored in localStorage (client-side)
- Secure cookies recommended for production

---

## Need Help?

- Check [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for deployment issues
- Review [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for setup verification
- Check backend logs: `python manage.py runserver --verbosity=2`
- Check frontend logs: Browser DevTools Console

**Last Updated**: September 3, 2026
