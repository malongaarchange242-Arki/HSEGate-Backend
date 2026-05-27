# Render Deployment Guide - CORS & Auth Fix

## ⚠️ Current Situation
The browser is getting **CORS errors (missing headers) + 500 errors** on login attempts from the deployed Render backend. This means:
1. **New code hasn't been deployed yet** - Or it was, but database connection is failing
2. **Database on Render might not be connected** - Check DATABASE_URL in Render environment

---

## 📋 Pre-Deployment Checklist

### 1. Test Locally First
```bash
cd d:\HSEGate-Backend

# Activate venv
.venv\Scripts\Activate.ps1

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test in browser:
- `http://localhost:8000/health` → Should return 200 OK with health status
- `http://localhost:8000/diagnostic` → Should show all routers loaded + database connected
- `http://localhost:8000/api/v1/auth/login` → Try POST with admin credentials

### 2. Verify .env File Has All Variables
```
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=your-secret-key
DEBUG=true (or false for production)
CORS_ORIGINS=["https://hsegate-frontend.onrender.com","https://hsegate-backend.onrender.com"]
```

---

## 🚀 Deploy to Render

### Step 1: Commit & Push Changes
```bash
git add app/main.py app/api/routes/auth.py HSEGate-Frontend/js/api.js
git commit -m "fix: CORS headers and auth error handling"
git push origin main
```

### Step 2: Verify Render Environment Variables
Go to **Render Dashboard** → **HSEGate Backend Service** → **Environment**

Ensure these are set:
- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `SECRET_KEY` - JWT secret
- ✅ `DEBUG` - `false` (or `true` for testing)
- ✅ `HOST` - `0.0.0.0`
- ✅ `PORT` - `8000`

### Step 3: Redeploy Service
In Render Dashboard:
1. Go to HSEGate Backend service
2. Click "Deploy latest commit" or wait for auto-deploy
3. Watch the deployment logs for:
   - ✅ `🔥 CORS enabled`
   - ✅ `✅ Database tables created/verified`
   - ✅ `🔐 Auth router registered`
   - ❌ Any errors with `Failed to load router`

---

## 🔍 Post-Deployment Verification

### Check Health Endpoint
Open in browser:
```
https://hsegate-backend.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "app": "HSEGate AI Backend",
  "version": "1.0.0",
  "database": "connected"
}
```

### Check Diagnostic Endpoint (Most Important)
Open in browser:
```
https://hsegate-backend.onrender.com/diagnostic
```

This shows:
- ✅ All routers loaded?
- ✅ Database connected?
- ✅ CORS enabled?
- ❌ Any connection errors?

**Example output if working:**
```json
{
  "database": {
    "connected": true,
    "error": null
  },
  "routers_loaded": {
    "auth": true,
    "workers": true,
    "incidents": true
  }
}
```

**If database is false:**
- ❌ DATABASE_URL is wrong or not set
- ❌ PostgreSQL server is down
- ❌ Network connectivity issue

---

## 🧪 Test Login Endpoint

### From Browser Console
```javascript
const body = JSON.stringify({
  email: 'admin@hsegate.com',
  password: 'admin123'
});

fetch('https://hsegate-backend.onrender.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: body
})
.then(r => r.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

**Expected:**
- ✅ `access_token` in response
- ✅ `token_type: "bearer"`

**If CORS error:**
- ❌ CORS not applied (need to redeploy)
- ❌ Render service not updated

**If 500 error:**
- ❌ Check `/diagnostic` endpoint for database error
- ❌ Check Render logs for exception

---

## 📊 Check Render Logs

In Render Dashboard → **HSEGate Backend** → **Logs**

Look for:
1. **🔥 CORS enabled** - Appears shortly after startup
2. **🔐 Auth router registered** - Confirms auth routes loaded
3. **❌ Failed to load router** - Indicates import error
4. **Database error** - Connection failure

---

## 🔧 If Still Getting CORS Errors After Deployment

### Problem: "No 'Access-Control-Allow-Origin' header"

1. **Verify frontend is using correct backend URL:**
   - Should be: `https://hsegate-backend.onrender.com`
   - Check browser console for: `📍 API URL: https://hsegate-backend.onrender.com/api/v1`

2. **Verify CORS_ORIGINS env var on Render:**
   - Include both: `https://hsegate-frontend.onrender.com` and `https://hsegate-backend.onrender.com`

3. **Hard refresh the frontend page:**
   - Ctrl+Shift+R (or Cmd+Shift+R on Mac)
   - Clear browser cache
   - Try in incognito/private window

4. **Check if Render redeployed successfully:**
   - Look at deployment log - should show "Build successful"
   - If deployment failed, check errors and fix

---

## 🚨 Debugging 500 Error on Login

If you're getting 500 errors, the issue is usually:

1. **Database not connected**
   - Check: `https://hsegate-backend.onrender.com/diagnostic`
   - Look for: `"database": {"connected": false}`
   - Fix: Verify `DATABASE_URL` in Render environment

2. **Admin user doesn't exist**
   - The default admin `admin@hsegate.com` must be in database
   - You need to seed the database after first deploy

3. **JWT configuration error**
   - Check: `SECRET_KEY` is set in Render environment
   - Check: `ALGORITHM=HS256` in settings

4. **Unhandled exception in login endpoint**
   - Check Render logs for full error traceback
   - Should show what's failing in the login function

---

## 📝 Next Steps

1. ✅ Commit and push the changes
2. ✅ Verify environment variables on Render
3. ✅ Redeploy the backend service
4. ✅ Check `/diagnostic` endpoint
5. ✅ Test login from browser console
6. ✅ If still failing, check Render logs
7. ✅ Monitor frontend dashboard for successful login

**Questions?** Check the logs at `/api/v1/auth/login` or Render dashboard logs tab.
