# Render Deployment Guide

This guide covers deploying the Movie App Backend and Frontend to Render.

## Prerequisites

- Render account (free or paid) at https://render.com
- GitHub repository for both backend and frontend
- GitHub connected to Render

## Backend Deployment

### Step 1: Prepare the Backend Repository

1. Ensure all the following files are in the root of the backend repository:
   - `Dockerfile` - Contains the production Docker image configuration
   - `render.yaml` - Render deployment configuration
   - `requirements.txt` - Python dependencies (includes gunicorn and whitenoise)
   - `.env.example` - Example environment variables
   - `.gitignore` - Should ignore `.env` files

2. Commit all changes:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 2: Deploy Backend on Render

1. Go to https://dashboard.render.com/

2. Click **New +** → **Web Service**

3. Connect your GitHub repository (if not already connected)

4. Select the backend repository

5. Fill in the configuration:
   - **Name**: `movie-app-api`
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Build Command**: (leave blank - uses Dockerfile)
   - **Start Command**: (leave blank - uses Dockerfile CMD)

6. Click **Create Web Service**

### Step 3: Configure Environment Variables

After the service is created, go to the **Environment** tab and add:

**Required Variables:**
- `DJANGO_SECRET_KEY`: Generate a secure key (e.g., using `django-insecure-...` or a proper secret)
- `DJANGO_DEBUG`: Set to `0` (for production)

**Database Variables** (should auto-populate if connected):
- `DB_ENGINE`: `postgresql`
- `DB_NAME`: `moviedb`
- `DB_USER`: (auto-populated)
- `DB_PASSWORD`: (auto-populated)
- `DB_HOST`: (auto-populated - should end with `.render.internal`)
- `DB_PORT`: `5432`

**Frontend Connection:**
- `CORS_ALLOWED_ORIGINS`: `https://movie-app-frontend.onrender.com,http://localhost:3000`
- `CORS_ALLOW_ALL_ORIGINS`: `False`

### Step 4: Deploy Database

1. In the **Environment** tab, you'll see a PostgreSQL database connection
2. Click the database link or create a new PostgreSQL database
3. Note the connection string - it will be automatically injected into environment variables

### Step 5: Test the Backend

Once deployed, test the API:
```
https://movie-app-api.onrender.com/api/
```

You should see the API documentation or schema.

---

## Frontend Deployment

### Step 1: Prepare the Frontend Repository

1. Update `.env` file (never commit this):
   ```env
   VITE_TMDB_API_KEY=your-tmdb-api-key
   VITE_BACKEND_API_URL=https://movie-app-api.onrender.com/api
   ```

2. Ensure `.env.example` exists with template values

3. Commit changes:
   ```bash
   git add .
   git commit -m "Update for Render deployment"
   git push origin main
   ```

### Step 2: Deploy Frontend on Render

1. Go to https://dashboard.render.com/

2. Click **New +** → **Static Site**

3. Connect your GitHub repository

4. Select the frontend repository

5. Fill in the configuration:
   - **Name**: `movie-app-frontend`
   - **Region**: Oregon (same as backend for lower latency)
   - **Branch**: `main`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

6. Click **Create Static Site**

### Step 3: Configure Environment Variables

For Render Static Sites, environment variables must be set at build time:

1. Go to **Environment** tab

2. Add:
   - `VITE_TMDB_API_KEY`: Your TMDB API key
   - `VITE_BACKEND_API_URL`: `https://movie-app-api.onrender.com/api`

### Step 4: Test the Frontend

Once deployed, visit:
```
https://movie-app-frontend.onrender.com
```

---

## Frontend-Backend Connection

The frontend uses a centralized API client (`src/services/backendApi.js`) that:
- Automatically handles JWT authentication
- Manages access tokens
- Provides organized endpoints for all API operations
- Handles CORS requests to the backend

### Using the Backend API in Components

```javascript
import backendApi from '@/services/backendApi';

// Login
const response = await backendApi.auth.login(email, password);
backendApi.setToken(response.access);

// Get user profile
const profile = await backendApi.users.getProfile(userId);

// Create a post
const post = await backendApi.posts.create({
  title: "My Movie Review",
  rating: 5,
  content: "Great movie!"
});
```

---

## Troubleshooting

### Backend Issues

**502 Bad Gateway**
- Check if the service is running: View logs in Render dashboard
- Verify `Dockerfile` has correct CMD
- Ensure Gunicorn is in `requirements.txt`

**Database Connection Failed**
- Verify database credentials in Environment variables
- Check if database service is running
- Ensure `DB_HOST` uses `.render.internal` for internal connection

**CORS Errors**
- Update `CORS_ALLOWED_ORIGINS` in environment variables
- Ensure frontend URL matches exactly

### Frontend Issues

**API Not Responding**
- Verify `VITE_BACKEND_API_URL` is correct (includes `/api` path)
- Check backend is running and accessible
- Look for CORS errors in browser DevTools

**Build Failures**
- Check build logs in Render dashboard
- Ensure all dependencies are in `package.json`
- Verify Node version compatibility

---

## Environment Variables Summary

### Backend (.env)
```
DJANGO_SECRET_KEY=<generate-a-secure-key>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,movie-app-api.onrender.com
DB_ENGINE=postgresql
DB_NAME=moviedb
DB_USER=<auto-from-db>
DB_PASSWORD=<auto-from-db>
DB_HOST=<auto-from-db>
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://movie-app-frontend.onrender.com,http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=False
```

### Frontend (.env)
```
VITE_TMDB_API_KEY=<your-tmdb-key>
VITE_BACKEND_API_URL=https://movie-app-api.onrender.com/api
```

---

## Next Steps

1. **Add SSL/HTTPS**: Render automatically provides SSL
2. **Custom Domain**: Configure custom domain in Render settings
3. **Monitor Performance**: Use Render's analytics dashboard
4. **Set up CI/CD**: Deployments auto-trigger on push to main branch
5. **Database Backups**: Configure automated backups for production database

---

## References

- [Render Documentation](https://render.com/docs)
- [Django Deployment](https://docs.djangoproject.com/en/latest/howto/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/)
- [CORS Headers Django](https://github.com/adamchainz/django-cors-headers)
