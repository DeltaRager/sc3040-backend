# SignLingo Backend - Render Deployment

## 🚀 Quick Deploy to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)

### Step 2: Deploy from GitHub
1. Push this folder to a GitHub repository
2. In Render dashboard, click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select this folder as the root directory

### Step 3: Configure Environment Variables
In Render dashboard, go to Environment tab and add:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Your API will be available at: `https://your-app-name.onrender.com`

## 📋 Manual Deploy (Alternative)

If you prefer manual upload:

1. **Create a new Web Service** in Render
2. **Choose "Build and deploy from a Git repository"**
3. **Connect your GitHub** and select this repository
4. **Configure:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11

## 🔧 Configuration Details

- **Free Tier**: 750 hours/month
- **Auto-sleep**: After 15 minutes of inactivity
- **Wake time**: ~30 seconds when accessed
- **HTTPS**: Automatically provided
- **Custom Domain**: Available (free)

## 🧪 Testing Your API

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Root endpoint
curl https://your-app-name.onrender.com/

# Public API
curl https://your-app-name.onrender.com/api/public
```

## 💡 Tips

1. **Keep it awake**: Use a service like UptimeRobot to ping your app every 14 minutes
2. **Environment variables**: Set them in Render dashboard, not in code
3. **Logs**: Check Render dashboard for deployment and runtime logs
4. **CORS**: Update `allowed_origins` in config.py for your frontend domain

## 🆘 Troubleshooting

- **Build fails**: Check requirements.txt and Python version
- **App crashes**: Check environment variables are set correctly
- **CORS errors**: Update allowed_origins in config.py
- **Slow startup**: Normal for free tier (cold starts)