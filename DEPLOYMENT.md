# 🚀 Deployment Guide - Smart Traffic Management System

This guide will help you deploy the Smart Traffic Management System to production using **Vercel** (frontend) and **Render** (backend).

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub repository with your code
- ✅ [Vercel Account](https://vercel.com/signup) (free)
- ✅ [Render Account](https://render.com/register) (free)
- ✅ [MongoDB Atlas Account](https://www.mongodb.com/cloud/atlas/register) (free)

---

## 🗄️ Step 1: Set Up MongoDB Atlas (Database)

### 1.1 Create MongoDB Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click **"Build a Database"** → Choose **FREE** (M0)
3. Select region closest to your backend (e.g., Singapore for Render)
4. Cluster name: `traffic-management`
5. Click **"Create Cluster"**

### 1.2 Configure Database Access

1. Go to **Database Access** → **Add New Database User**
   - Username: `traffic_admin`
   - Password: Generate secure password (save it!)
   - Privileges: **Atlas Admin**
2. Click **"Add User"**

### 1.3 Configure Network Access

1. Go to **Network Access** → **Add IP Address**
2. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Required for Render to connect
3. Click **"Confirm"**

### 1.4 Get Connection String

1. Go to **Database** → Click **"Connect"**
2. Choose **"Connect your application"**
3. Copy the connection string:
   ```
   mongodb+srv://traffic_admin:<password>@traffic-management.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual password
5. Save this for later!

---

## 🖥️ Step 2: Deploy Backend to Render

### 2.1 Prepare Backend

1. Open your project in VS Code
2. Navigate to `minor_real/backend/`
3. Create `.env` file (copy from `.env.example`):
   ```env
   MONGODB_URL=mongodb+srv://traffic_admin:YOUR_PASSWORD@traffic-management.xxxxx.mongodb.net/traffic_management?retryWrites=true&w=majority
   YOLO_MODEL_PATH=./data/models/yolov8n.pt
   DEBUG=false
   ```

### 2.2 Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `traffic-management-backend`
   - **Region**: Singapore (or closest)
   - **Branch**: `master`
   - **Root Directory**: `minor_real/backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. **Environment Variables** (click "Advanced"):
   ```
   MONGODB_URL = mongodb+srv://traffic_admin:PASSWORD@....mongodb.net/traffic_management
   DEBUG = false
   YOLO_MODEL_PATH = ./data/models/yolov8n.pt
   YOLO_CONFIDENCE = 0.15
   VIDEO_INPUT_PATH = ./data/videos
   VIDEO_OUTPUT_PATH = ./data/outputs
   MIN_GREEN_TIME = 15
   MAX_GREEN_TIME = 120
   DEFAULT_GREEN_TIME = 30
   CONGESTION_THRESHOLD = 20
   SECRET_KEY = <generate-random-string>
   ALLOWED_ORIGINS = *
   ```

6. Click **"Create Web Service"**
7. Wait for deployment (~5-10 minutes)
8. Copy your backend URL: `https://traffic-management-backend.onrender.com`

### 2.3 Test Backend

Visit: `https://your-backend-url.onrender.com/`

Should return:
```json
{
  "message": "Traffic Management System API",
  "version": "1.0.0",
  "status": "operational"
}
```

API Docs: `https://your-backend-url.onrender.com/docs`

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Prepare Frontend

1. Navigate to `minor_real/frontend/`
2. Create `.env.local` file:
   ```env
   VITE_API_URL=https://traffic-management-backend.onrender.com/api/v1
   ```

### 3.2 Deploy to Vercel

#### Option A: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd minor_real/frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Option B: Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `minor_real/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Environment Variables**:
   ```
   VITE_API_URL = https://traffic-management-backend.onrender.com/api/v1
   ```

6. Click **"Deploy"**
7. Wait for deployment (~2-3 minutes)
8. Copy your frontend URL: `https://your-project.vercel.app`

---

## 🔧 Step 4: Configure CORS

### 4.1 Update Backend CORS Settings

1. Go to your Render dashboard
2. Select your backend service
3. Add environment variable:
   ```
   ALLOWED_ORIGINS = https://your-project.vercel.app,http://localhost:5173
   ```
4. Or edit `minor_real/backend/app/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-project.vercel.app",
           "http://localhost:5173",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
5. Commit and push changes
6. Render will auto-redeploy

---

## ✅ Step 5: Verify Deployment

### 5.1 Test Checklist

- [ ] Backend health check: `https://your-backend.onrender.com/`
- [ ] API docs accessible: `https://your-backend.onrender.com/docs`
- [ ] Frontend loads: `https://your-project.vercel.app`
- [ ] Frontend can connect to backend (check browser console)
- [ ] MongoDB connection works (check Render logs)
- [ ] Dashboard displays without errors

### 5.2 Check Logs

**Render Backend Logs:**
1. Go to Render dashboard → Your service
2. Click **"Logs"** tab
3. Look for:
   ```
   ✓ MongoDB connected
   ✓ Vehicle Detector initialized
   ✓ Application started successfully
   ```

**Vercel Frontend Logs:**
1. Go to Vercel dashboard → Your project
2. Click **"Deployments"** → Latest deployment
3. Check build logs for errors

---

## 🎯 Step 6: Post-Deployment Configuration

### 6.1 Update GitHub Repository

1. Add deployment URLs to README.md:
   ```markdown
   ## 🌐 Live Demo
   
   - **Frontend**: https://your-project.vercel.app
   - **Backend API**: https://traffic-management-backend.onrender.com
   - **API Docs**: https://traffic-management-backend.onrender.com/docs
   ```

2. Commit and push

### 6.2 Configure Custom Domain (Optional)

**Vercel:**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

**Render:**
1. Go to Service Settings → Custom Domain
2. Add your custom domain
3. Update DNS records

---

## 🔒 Security Considerations

### Production Checklist

- [ ] **Environment Variables**: All secrets in env vars (not in code)
- [ ] **MongoDB**: IP whitelist enabled (Render IPs)
- [ ] **CORS**: Only allow your frontend domain
- [ ] **SECRET_KEY**: Use strong random string
- [ ] **DEBUG**: Set to `false` in production
- [ ] **HTTPS**: Enabled by default on Vercel/Render
- [ ] **Rate Limiting**: Consider adding rate limiting middleware
- [ ] **MongoDB Backup**: Enable automatic backups in Atlas

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Frontend can't connect to backend**
- Check CORS settings in backend
- Verify `VITE_API_URL` in Vercel environment variables
- Check browser console for CORS errors

#### 2. **Backend deployment fails**
- Check `requirements.txt` is complete
- Verify Python version compatibility
- Check Render logs for specific errors

#### 3. **MongoDB connection fails**
- Verify connection string is correct
- Check MongoDB Atlas network access (allow 0.0.0.0/0)
- Ensure database user has correct permissions

#### 4. **YOLO model download fails**
- Check Render disk space (512 MB on free tier)
- Model auto-downloads on first run
- May take 2-3 minutes on cold start

#### 5. **Render service sleeps (free tier)**
- Free tier sleeps after 15 min inactivity
- First request takes ~30-60 seconds to wake up
- Consider paid tier for production use

---

## 💰 Cost Breakdown

### Free Tier Limits

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Vercel** | ✅ Free | 100 GB bandwidth/month, unlimited sites |
| **Render** | ✅ Free | 750 hours/month, 512 MB RAM, sleeps after 15 min |
| **MongoDB Atlas** | ✅ Free | 512 MB storage, shared cluster |

### Recommended Paid Tiers (Production)

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| **Vercel Pro** | $20/month | Unlimited bandwidth, better performance |
| **Render Starter** | $7/month | No sleep, 512 MB RAM, always-on |
| **MongoDB M10** | $10/month | 10 GB storage, backups, better performance |

**Total Production Cost: ~$37/month**

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Both Vercel and Render support automatic deployments:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin master
   ```

2. **Automatic Deployment**:
   - Vercel: Deploys frontend automatically
   - Render: Deploys backend automatically

3. **Monitor Deployments**:
   - Check Vercel/Render dashboards
   - Review deployment logs
   - Test changes on production URLs

---

## 📊 Monitoring & Analytics

### Set Up Monitoring

1. **Vercel Analytics** (Built-in):
   - Enable in Project Settings → Analytics
   - Track page views, performance

2. **Render Metrics**:
   - View CPU, Memory, Response times
   - Available in dashboard

3. **MongoDB Monitoring**:
   - Atlas dashboard shows queries, connections
   - Set up alerts for issues

---

## 🎉 You're Live!

Your Smart Traffic Management System is now deployed to production! 🚀

**Share your deployed app:**
- Frontend: `https://your-project.vercel.app`
- API Docs: `https://your-backend.onrender.com/docs`

For questions or issues, check the logs or refer to:
- [Vercel Docs](https://vercel.com/docs)
- [Render Docs](https://render.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
