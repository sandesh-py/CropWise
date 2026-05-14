# CropWise Deployment Guide

This guide covers deploying CropWise to production. We'll deploy the frontend and backend separately for better scalability.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Environment Variables](#environment-variables)
5. [Production Configuration](#production-configuration)
6. [Alternative Deployment Options](#alternative-deployment-options)

---

## Prerequisites

Before deploying, ensure you have:
- ✅ Git repository (GitHub/GitLab/Bitbucket)
- ✅ API Keys:
  - OpenWeatherMap API Key
  - Google Gemini API Key
- ✅ Python 3.8+ installed locally
- ✅ Node.js 16+ installed locally

---

## Backend Deployment

### Option 1: Railway (Recommended - Easy & Free Tier Available)

1. **Sign up at [Railway.app](https://railway.app)**

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (connect your GitHub account)
   - Select your CropWise repository

3. **Configure Backend Service**
   - Railway will auto-detect Python
   - Set Root Directory: `backend`
   - Set Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Add Environment Variables** (in Railway dashboard):
   ```
   OPENWEATHER_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   MONGO_URI=your_mongodb_uri (optional, if using MongoDB)
   PORT=8000
   FLASK_ENV=production
   ```

5. **Create requirements.txt for production** (if not exists):
   ```bash
   cd backend
   pip freeze > requirements.txt
   ```

6. **Add Procfile** (create `backend/Procfile`):
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```

7. **Deploy**
   - Railway will automatically deploy on push to main branch
   - Get your backend URL (e.g., `https://cropwise-backend.railway.app`)

---

### Option 2: Render

1. **Sign up at [Render.com](https://render.com)**

2. **Create New Web Service**
   - Connect your GitHub repository
   - Select "Web Service"
   - Choose your repository

3. **Configure Service**
   - **Name**: `cropwise-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**:
   ```
   OPENWEATHER_API_KEY
   GEMINI_API_KEY
   MONGO_URI (optional)
   PORT=8000
   ```

5. **Deploy**
   - Render will build and deploy automatically
   - Get your backend URL (e.g., `https://cropwise-backend.onrender.com`)

---

### Option 3: Heroku

1. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku App**:
   ```bash
   cd backend
   heroku create cropwise-backend
   ```

4. **Add Buildpacks**:
   ```bash
   heroku buildpacks:add heroku/python
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set OPENWEATHER_API_KEY=your_key
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set FLASK_ENV=production
   ```

6. **Create Procfile** (`backend/Procfile`):
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
   ```

7. **Deploy**:
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

---

## Frontend Deployment

### Option 1: Vercel (Recommended - Best for React/Vite)

1. **Sign up at [Vercel.com](https://vercel.com)**

2. **Import Project**
   - Click "Add New Project"
   - Import from GitHub
   - Select your CropWise repository

3. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

5. **Update API Configuration**
   
   Update `frontend/src/services/api.js` to use environment variable:
   ```javascript
   const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```

6. **Deploy**
   - Vercel will automatically deploy
   - Get your frontend URL (e.g., `https://cropwise.vercel.app`)

---

### Option 2: Netlify

1. **Sign up at [Netlify.com](https://netlify.com)**

2. **Add New Site**
   - "Add new site" → "Import an existing project"
   - Connect to GitHub and select repository

3. **Configure Build Settings**:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

4. **Add Environment Variables**:
   - Go to Site settings → Environment variables
   - Add: `VITE_API_URL` = `https://your-backend-url.com`

5. **Deploy**
   - Netlify will build and deploy automatically

---

### Option 3: GitHub Pages (Static Hosting)

1. **Update vite.config.js**:
   ```javascript
   export default defineConfig({
     plugins: [react()],
     base: '/cropwise/', // Your repo name
     // ... rest of config
   })
   ```

2. **Install gh-pages**:
   ```bash
   cd frontend
   npm install --save-dev gh-pages
   ```

3. **Add to package.json**:
   ```json
   {
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d dist"
     }
   }
   ```

4. **Deploy**:
   ```bash
   npm run deploy
   ```

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the `backend` directory (for local) or set in your hosting platform:

```env
# Required
OPENWEATHER_API_KEY=your_openweather_api_key
GEMINI_API_KEY=your_gemini_api_key

# Optional
MONGO_URI=mongodb://localhost:27017/cropwise
FLASK_ENV=production
PORT=8000

# CORS (if needed)
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### Frontend Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=https://your-backend-url.railway.app
```

**Important**: Vite requires `VITE_` prefix for environment variables to be exposed to the client.

---

## Production Configuration

### 1. Update Backend CORS Settings

Update `backend/app.py`:

```python
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow specific origins in production
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, origins=[os.getenv('CORS_ORIGINS', 'https://your-frontend-url.vercel.app')])
else:
    CORS(app)  # Allow all in development
```

### 2. Update Frontend API Service

Update `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiService = {
  // ... existing code
  async getCurrentWeather(city) {
    const response = await fetch(`${API_BASE_URL}/api/weather/${city}`);
    // ... rest of code
  },
  // ... update all API calls to use API_BASE_URL
};
```

### 3. Add Gunicorn to Backend Requirements

Ensure `backend/requirements.txt` includes:

```
gunicorn>=21.2.0
```

### 4. Create Production Build Scripts

**Backend** - Create `backend/start.sh`:
```bash
#!/bin/bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
```

**Frontend** - Build command:
```bash
cd frontend
npm run build
```

---

## Step-by-Step Deployment Checklist

### Backend Deployment

- [ ] Push code to GitHub
- [ ] Create account on Railway/Render/Heroku
- [ ] Create new project/service
- [ ] Set root directory to `backend`
- [ ] Add all environment variables
- [ ] Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- [ ] Deploy and get backend URL
- [ ] Test backend API endpoints

### Frontend Deployment

- [ ] Update `frontend/src/services/api.js` to use environment variable
- [ ] Create `.env` file with `VITE_API_URL`
- [ ] Push code to GitHub
- [ ] Create account on Vercel/Netlify
- [ ] Import project from GitHub
- [ ] Set root directory to `frontend`
- [ ] Add environment variable `VITE_API_URL`
- [ ] Set build command: `npm run build`
- [ ] Set output directory: `dist`
- [ ] Deploy and get frontend URL
- [ ] Update backend CORS with frontend URL
- [ ] Test full application

---

## Alternative Deployment Options

### Docker Deployment

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml** (root directory):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### AWS Deployment

- **Backend**: AWS Elastic Beanstalk or EC2
- **Frontend**: AWS S3 + CloudFront
- **Database**: AWS RDS (if using MongoDB Atlas)

### Google Cloud Deployment

- **Backend**: Cloud Run or App Engine
- **Frontend**: Firebase Hosting or Cloud Storage
- **Database**: MongoDB Atlas or Firestore

---

## Post-Deployment

### 1. Test All Features
- [ ] Crop prediction works
- [ ] Weather data loads
- [ ] Chatbot responds
- [ ] Analytics displays correctly
- [ ] SHAP explanations show

### 2. Monitor Performance
- Set up error tracking (Sentry, LogRocket)
- Monitor API response times
- Check server logs regularly

### 3. Set Up Custom Domain (Optional)
- **Vercel**: Add domain in project settings
- **Railway**: Use Railway's domain or add custom domain
- Update CORS settings with new domain

### 4. Enable HTTPS
- Most platforms (Vercel, Railway, Render) provide HTTPS automatically
- Ensure all API calls use HTTPS in production

---

## Troubleshooting

### Backend Issues

**Issue**: CORS errors
- **Solution**: Update CORS settings in `app.py` with frontend URL

**Issue**: Environment variables not loading
- **Solution**: Check variable names match exactly (case-sensitive)

**Issue**: Gunicorn not found
- **Solution**: Add `gunicorn` to `requirements.txt` and redeploy

### Frontend Issues

**Issue**: API calls failing
- **Solution**: Check `VITE_API_URL` is set correctly
- **Solution**: Verify backend URL is accessible

**Issue**: Build fails
- **Solution**: Check Node.js version (should be 16+)
- **Solution**: Clear `node_modules` and reinstall

**Issue**: Environment variables not working
- **Solution**: Ensure variables start with `VITE_` prefix
- **Solution**: Rebuild after adding variables

---

## Quick Deploy Commands

### Railway (Backend)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
cd backend
railway init

# Deploy
railway up
```

### Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

---

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review error logs in platform dashboard
3. Test locally first with production environment variables
4. Verify all environment variables are set correctly

---

## Recommended Setup

**Best for Beginners**:
- Backend: Railway (easiest setup, free tier)
- Frontend: Vercel (automatic deployments, free tier)

**Best for Production**:
- Backend: Railway or Render (good performance, reasonable pricing)
- Frontend: Vercel (CDN, fast global delivery)

**Best for Cost**:
- Backend: Railway free tier or Render free tier
- Frontend: Vercel free tier or Netlify free tier

---

Good luck with your deployment! 🚀

