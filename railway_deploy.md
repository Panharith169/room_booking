# Deploy to Railway (FREE & EASY)

## Step 1: Prepare Your Project
1. Create a GitHub repository
2. Push your code to GitHub

## Step 2: Setup Railway
1. Go to https://railway.app
2. Sign up with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your room booking repository

## Step 3: Environment Variables
Add these in Railway dashboard:
- `DEBUG=False`
- `ALLOWED_HOSTS=*.railway.app`
- `SECRET_KEY=your-secret-key-here`

## Step 4: Database
Railway will automatically provide PostgreSQL database

## Your app will be live at: https://your-project-name.railway.app

## Benefits:
✅ FREE hosting
✅ Automatic HTTPS
✅ Global access
✅ Easy deployment
✅ Free PostgreSQL database
