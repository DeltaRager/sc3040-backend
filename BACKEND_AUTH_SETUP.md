# Backend Authentication Setup with Publishable Key

This guide explains how to set up authentication for your FastAPI backend using Supabase's publishable key instead of the service role key.

## 🔧 **Environment Variables Setup**

### **1. Get Your Supabase Keys**

1. **Go to your Supabase Dashboard**
2. **Navigate to Settings → API**
3. **Copy the following values:**
   - `Project URL` (e.g., `https://your-project.supabase.co`)
   - `Publishable Key` (public key)
   - `JWT Secret` (from the JWT Settings section)

### **2. Create Backend Environment File**

Create a `.env` file in your `App/backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here

# FastAPI Configuration
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

### **3. Alternative: Use Environment Variables Directly**

You can also set these as system environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_PUBLISHABLE_KEY="your_publishable_key_here"
export SUPABASE_JWT_SECRET="your_jwt_secret_here"
```

## 🔐 **How Authentication Works**

### **1. Token Verification Process**

1. **Frontend** sends JWT token in `Authorization: Bearer {token}` header
2. **Backend** extracts token from request
3. **Backend** verifies token using Supabase JWT secret
4. **Backend** extracts user data from verified token payload
5. **Backend** returns user information or 401 if invalid

### **2. Security Benefits**

✅ **No Admin Privileges**: Publishable key has limited permissions  
✅ **JWT Verification**: Tokens are cryptographically verified  
✅ **No Database Calls**: Token verification doesn't require Supabase API calls  
✅ **Better Performance**: Faster than service role key verification  

## 🚀 **Testing the Setup**

### **1. Start the Backend**

```bash
cd App/backend
pip install -r requirements.txt
python main.py
```

### **2. Test with Frontend**

1. **Start your frontend**: `npm run dev`
2. **Visit**: `http://localhost:3000/main/api-example`
3. **Test authenticated endpoints** to verify JWT verification works

### **3. Test with curl**

```bash
# Get token from frontend (check browser dev tools)
TOKEN="your_jwt_token_here"

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/profile
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"JWT secret not configured"**
   - Make sure `SUPABASE_JWT_SECRET` is set in your `.env` file
   - Verify the JWT secret is correct from Supabase dashboard

2. **"Invalid or expired token"**
   - Check if the token is valid and not expired
   - Ensure the token is properly formatted in the Authorization header

3. **"Invalid token payload"**
   - The token might be malformed or from a different Supabase project
   - Verify you're using the correct JWT secret

### **Debug Mode**

Add this to your backend to see detailed error logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 **Key Differences from Service Role Key**

| Aspect | Service Role Key | Publishable Key |
|--------|------------------|-----------------|
| **Permissions** | Admin (full access) | Limited (public access) |
| **Token Verification** | `supabase.auth.get_user()` | Manual JWT verification |
| **Security** | High risk if exposed | Safer for client-side use |
| **Performance** | Requires API call | Local verification only |
| **Setup** | Simple | Requires JWT secret |

## ✅ **Verification Checklist**

- [ ] `SUPABASE_URL` is set correctly
- [ ] `SUPABASE_PUBLISHABLE_KEY` is set correctly  
- [ ] `SUPABASE_JWT_SECRET` is set correctly
- [ ] Backend starts without errors
- [ ] Protected endpoints return 401 without token
- [ ] Protected endpoints return user data with valid token
- [ ] Frontend can make authenticated requests successfully

## 🔄 **Migration from Service Role Key**

If you were previously using the service role key:

1. **Update environment variables** (remove service role key)
2. **Update config.py** (already done)
3. **Update auth.py** (already done)
4. **Test all protected endpoints**
5. **Update deployment environment variables**

The authentication system is now more secure and follows Supabase best practices!
