# Docker Setup for SignLingo Backend

This guide explains how to run the SignLingo backend using Docker with the updated authentication system.

## 🔧 **Environment Variables Setup**

### **1. Create Environment File**

Create a `.env` file in `App/backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here

# FastAPI Configuration
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

### **2. Get Your Supabase Keys**

1. **Go to your Supabase Dashboard**
2. **Navigate to Settings → API**
3. **Copy the following values:**
   - `Project URL` → `SUPABASE_URL`
   - `Publishable Key` → `SUPABASE_PUBLISHABLE_KEY`
   - `JWT Secret` (from JWT Settings) → `SUPABASE_JWT_SECRET`

## 🐳 **Docker Commands**

### **Development Mode (Hot Reload)**

```bash
# Build and run with hot reload
docker-compose --profile dev up --build

# Run in background
docker-compose --profile dev up -d --build

# View logs
docker-compose --profile dev logs -f

# Stop
docker-compose --profile dev down
```

### **Production Mode (With Nginx)**

```bash
# Build and run production setup
docker-compose --profile production up --build

# Run in background
docker-compose --profile production up -d --build

# View logs
docker-compose --profile production logs -f

# Stop
docker-compose --profile production down
```

### **Individual Service Commands**

```bash
# Build only the backend
docker-compose build signlingo-backend

# Run only the backend (development)
docker-compose --profile dev up signlingo-backend

# Run only the backend (production)
docker-compose --profile production up signlingo-backend-prod
```

## 🔍 **Health Checks**

### **Backend Health Check**

```bash
# Check if backend is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "environment": "development"}
```

### **Docker Health Check**

The Docker container includes automatic health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect <container_id> | grep -A 10 "Health"
```

## 🚀 **Quick Start**

### **1. Development Setup**

```bash
# 1. Create .env file with your Supabase credentials
cd App/backend
cp .env.example .env  # Edit with your actual values

# 2. Start development environment
docker-compose --profile dev up --build

# 3. Test the API
curl http://localhost:8000/health
```

### **2. Production Setup**

```bash
# 1. Create .env file with production values
cd App/backend
cp .env.example .env  # Edit with your actual values

# 2. Start production environment
docker-compose --profile production up --build

# 3. Access via Nginx (port 80)
curl http://localhost/health
```

## 🔧 **Configuration Details**

### **Development Profile**
- **Hot reload**: Code changes automatically restart the server
- **Volume mounting**: Local code is mounted into container
- **Debug mode**: Detailed error messages and logging
- **Port**: 8000 (direct access to FastAPI)

### **Production Profile**
- **Nginx reverse proxy**: Handles static files and load balancing
- **Health checks**: Automatic container health monitoring
- **Restart policy**: Automatically restarts on failure
- **Port**: 80 (via Nginx) and 8000 (direct FastAPI)

## 🐛 **Troubleshooting**

### **Common Issues**

1. **"Environment variable not set"**
   ```bash
   # Check if .env file exists and has correct values
   cat .env
   
   # Verify environment variables are loaded
   docker-compose config
   ```

2. **"Port already in use"**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Stop conflicting services
   docker-compose down
   ```

3. **"Health check failed"**
   ```bash
   # Check container logs
   docker-compose logs signlingo-backend
   
   # Test health endpoint manually
   curl http://localhost:8000/health
   ```

4. **"Authentication errors"**
   - Verify `SUPABASE_JWT_SECRET` is correct
   - Check that `SUPABASE_PUBLISHABLE_KEY` matches your project
   - Ensure `SUPABASE_URL` is the correct project URL

### **Debug Commands**

```bash
# View all environment variables
docker-compose config

# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 -f

# Execute shell in running container
docker-compose exec signlingo-backend bash

# Rebuild without cache
docker-compose build --no-cache
```

## 📝 **Environment Variables Reference**

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_PUBLISHABLE_KEY` | Public publishable key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_JWT_SECRET` | JWT signing secret | `your-jwt-secret-here` |
| `SECRET_KEY` | FastAPI secret key | `your-secret-key-here` |
| `ENVIRONMENT` | Environment mode | `development` or `production` |

## ✅ **Verification Checklist**

- [ ] `.env` file created with correct Supabase credentials
- [ ] Docker and Docker Compose installed
- [ ] Backend starts without errors (`docker-compose --profile dev up`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend can connect to backend API
- [ ] Authentication works with JWT tokens
- [ ] Production setup works with Nginx

Your Docker setup is now ready with the updated authentication system!
