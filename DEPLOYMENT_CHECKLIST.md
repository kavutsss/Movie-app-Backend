# Deployment Checklist

This checklist ensures both the backend and frontend are properly configured and deployed on Render.

## Backend Deployment Checklist

### Configuration Files ✓
- [x] `Dockerfile` - Updated to use Gunicorn with proper production settings
- [x] `requirements.txt` - Contains:
  - [x] gunicorn
  - [x] whitenoise
  - [x] psycopg2-binary (for PostgreSQL)
  - [x] python-dotenv
  - [x] django-cors-headers
  - [x] djangorestframework-simplejwt
  - [x] All other dependencies
- [x] `render.yaml` - Complete Render deployment configuration
- [x] `.env.example` - Template for environment variables
- [x] `.gitignore` - Excludes `.env` files

### Settings Configuration ✓
- [x] `config/settings.py` contains:
  - [x] Whitenoise middleware for static files
  - [x] CORS headers middleware
  - [x] Environment-based SECRET_KEY
  - [x] DEBUG set from environment variable
  - [x] ALLOWED_HOSTS configured from environment
  - [x] PostgreSQL database configuration
  - [x] JWT authentication for REST API
  - [x] CORS_ALLOWED_ORIGINS configured
  - [x] STATIC_ROOT and STATICFILES_STORAGE for production
  - [x] Production security settings (SSL, HSTS, etc.)

### Database ✓
- [x] PostgreSQL configured (using environment variables)
- [x] Database migrations included in Dockerfile startup
- [x] Using `.render.internal` for internal database connection

### API Endpoints ✓
- [x] `accounts` app - User authentication and profiles
- [x] `posts` app - Post creation, comments, likes
- [x] `clubs` app - Club management and membership
- [x] `watchlist` app - User watchlist functionality
- [x] API schema available at `/api/`

### Security ✓
- [x] CSRF protection enabled
- [x] CORS properly configured
- [x] JWT token authentication
- [x] Production SSL/HTTPS settings when DEBUG=0
- [x] Sensitive data in environment variables (not hardcoded)

### Git Status
- [ ] All changes committed: `git add . && git commit -m "Prepare for Render deployment"`
- [ ] Pushed to main branch: `git push origin main`

---

## Frontend Deployment Checklist

### Configuration Files ✓
- [x] `.env` - Contains:
  - [x] VITE_TMDB_API_KEY (from your TMDB account)
  - [x] VITE_BACKEND_API_URL (set to http://localhost:8000/api for dev)
- [x] `.env.example` - Template for environment variables

### Build Configuration ✓
- [x] `package.json` - Contains build script: `npm run build`
- [x] `vite.config.js` - Configured for React
- [x] All dependencies installed: `npm install`
- [x] Build output directory: `dist/`

### API Integration ✓
- [x] `src/services/backendApi.js` - Created with:
  - [x] Centralized API client
  - [x] JWT token management
  - [x] Auth endpoints
  - [x] User endpoints
  - [x] Posts endpoints
  - [x] Comments endpoints
  - [x] Clubs endpoints
  - [x] Watchlist endpoints
  - [x] Error handling and CORS support

### Environment Variables Ready
- [ ] Set `VITE_BACKEND_API_URL` in Render environment to backend API URL
- [ ] Backend URL format: `https://movie-app-api.onrender.com/api`

### Git Status
- [ ] All changes committed
- [ ] Pushed to main branch

---

## Render Deployment Steps

### Backend Service
1. [ ] Create New Web Service on Render
   - [ ] Connect GitHub repository
   - [ ] Select backend repo
   - [ ] Runtime: Docker
   - [ ] Region: Oregon
   
2. [ ] Set Environment Variables
   - [ ] DJANGO_SECRET_KEY=`<generate>`
   - [ ] DJANGO_DEBUG=0
   - [ ] CORS_ALLOWED_ORIGINS=`https://movie-app-frontend.onrender.com`
   
3. [ ] Create PostgreSQL Database
   - [ ] Name: moviedb
   - [ ] Same region as backend
   
4. [ ] Deploy and Verify
   - [ ] Service builds successfully
   - [ ] Database migrations run
   - [ ] Health check passes
   - [ ] API accessible at https://movie-app-api.onrender.com/api/

### Frontend Service
1. [ ] Create New Static Site on Render
   - [ ] Connect GitHub repository
   - [ ] Select frontend repo
   - [ ] Build Command: `npm install && npm run build`
   - [ ] Publish Directory: `dist`
   - [ ] Region: Oregon (same as backend)
   
2. [ ] Set Environment Variables
   - [ ] VITE_TMDB_API_KEY=`<your-key>`
   - [ ] VITE_BACKEND_API_URL=`https://movie-app-api.onrender.com/api`
   
3. [ ] Deploy and Verify
   - [ ] Site builds successfully
   - [ ] Site accessible at https://movie-app-frontend.onrender.com
   - [ ] API calls work from frontend

---

## Post-Deployment Testing

### Backend API Tests
- [ ] Health check: `GET https://movie-app-api.onrender.com/api/`
- [ ] Schema available: `GET https://movie-app-api.onrender.com/api/schema/`
- [ ] Database connected (check logs for migration success)

### Frontend Tests
- [ ] Site loads at https://movie-app-frontend.onrender.com
- [ ] TMDB API calls work (trending movies display)
- [ ] Backend API calls work (no 404 or CORS errors)
  - Test with: Open browser DevTools → Network/Console
- [ ] Authentication flow works (if implemented)

### Connection Tests
```bash
# Test backend health
curl https://movie-app-api.onrender.com/api/

# Test frontend (should see HTML)
curl https://movie-app-frontend.onrender.com
```

---

## Troubleshooting

### Backend Won't Start
- [ ] Check Render logs for errors
- [ ] Verify Dockerfile CMD syntax
- [ ] Ensure gunicorn is in requirements.txt
- [ ] Check database connection string

### Frontend Build Fails
- [ ] Check "Build & Deploys" logs
- [ ] Verify all dependencies in package.json
- [ ] Ensure build script works locally
- [ ] Check Node version compatibility

### API Calls Fail (CORS)
- [ ] Verify VITE_BACKEND_API_URL is correct
- [ ] Check CORS_ALLOWED_ORIGINS in backend
- [ ] Ensure backend is running
- [ ] Check browser console for specific error

### Database Errors
- [ ] Verify database service is running
- [ ] Check DB_HOST uses .render.internal
- [ ] Verify credentials match database settings
- [ ] Check migrations ran successfully

---

## Environment Variables Reference

### Backend Required (Render Environment)
```
DJANGO_SECRET_KEY=<generate-strong-key>
DJANGO_DEBUG=0
DB_ENGINE=postgresql
DB_NAME=moviedb
DB_USER=<auto>
DB_PASSWORD=<auto>
DB_HOST=<auto>
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://movie-app-frontend.onrender.com
CORS_ALLOW_ALL_ORIGINS=False
```

### Frontend Required (Render Environment)
```
VITE_TMDB_API_KEY=<your-key>
VITE_BACKEND_API_URL=https://movie-app-api.onrender.com/api
```

---

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Vite Build Guide](https://vitejs.dev/guide/build.html)
- [CORS Configuration](https://github.com/adamchainz/django-cors-headers)

---

**Last Updated**: September 3, 2026
**Status**: Ready for Deployment ✓
