# 🚀 Quick Deploy Guide - Testing Mode (No Database Required)

This guide shows how to deploy the **Smart Traffic Management System** for testing/demo purposes **without MongoDB**.

---

## 🎯 What You'll Get

✅ **Full backend API running on Render** (in-memory database)  
✅ **Frontend UI on Vercel**  
✅ **All endpoints working** (data stored temporarily in memory)  
✅ **Perfect for demonstrations and testing**  

⚠️ **Limitations:**
- Data is lost when backend restarts (Render free tier restarts after 15 min idle)
- No persistent storage
- Good for demos, not production use

---

## 📦 Step 1: Deploy Backend to Render (5 minutes)

### Option A: Using render.yaml (Easiest)

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Swayam7Garg/smart-traffic-monitoring`
4. Render will auto-detect `render.yaml`
5. Click **"Apply"** - it will use settings from render.yaml
6. Click **"Create Web Service"**

**That's it!** Backend will deploy with mock database automatically.

### Option B: Manual Configuration

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. **Configure:**
   ```
   Name: traffic-backend-demo
   Region: Singapore (or closest)
   Branch: master
   Root Directory: minor_real/backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

5. **Environment Variables:**
   ```
   USE_MOCK_DB = true
   YOLO_MODEL_PATH = ./data/models/yolov8n.pt
   YOLO_CONFIDENCE = 0.15
   DEBUG = false
   SECRET_KEY = <generate-random-string>
   ALLOWED_ORIGINS = *
   ```

6. Click **"Create Web Service"**

### Wait for Deployment (~5-8 minutes)

Watch the logs, you should see:
```
✓ Mock Database initialized: traffic_management
✓ Vehicle Detector initialized
✓ Application started successfully
🚦 Traffic Management System Ready
```

**Copy your backend URL:** `https://traffic-backend-demo.onrender.com`

---

## 🌐 Step 2: Deploy Frontend to Vercel (3 minutes)

### Option A: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd minor_real/frontend

# Login
vercel login

# Deploy
vercel --prod
```

**When prompted for environment variables:**
```
VITE_API_URL = https://traffic-backend-demo.onrender.com/api/v1
```

### Option B: Vercel Dashboard

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repo: `Swayam7Garg/smart-traffic-monitoring`
4. **Configure:**
   ```
   Framework Preset: Vite
   Root Directory: minor_real/frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Environment Variables:**
   ```
   VITE_API_URL = https://traffic-backend-demo.onrender.com/api/v1
   ```

6. Click **"Deploy"**

**Your app will be live at:** `https://your-project.vercel.app`

---

## ✅ Step 3: Update CORS

1. Go to Render Dashboard → Your service
2. Go to **Environment** tab
3. Update **ALLOWED_ORIGINS:**
   ```
   ALLOWED_ORIGINS = https://your-project.vercel.app,http://localhost:5173
   ```
4. Click **"Save Changes"** (backend will auto-redeploy)

---

## 🎉 You're Live!

### Test Your Deployment:

1. **Backend Health:**
   ```
   https://traffic-backend-demo.onrender.com/
   ```
   Should return:
   ```json
   {
     "message": "Traffic Management System API",
     "version": "1.0.0",
     "status": "operational"
   }
   ```

2. **API Documentation:**
   ```
   https://traffic-backend-demo.onrender.com/docs
   ```

3. **Frontend:**
   ```
   https://your-project.vercel.app
   ```

---

## 📊 What Works in Mock Mode

✅ **Camera Management:** Add/view/edit cameras (stored in memory)  
✅ **Video Upload:** Upload and process videos  
✅ **Vehicle Detection:** YOLOv8 detects vehicles in real-time  
✅ **Analytics:** View traffic statistics  
✅ **Signal Control:** Adaptive signal timing  
✅ **Emergency System:** Emergency vehicle priority  
✅ **All API Endpoints:** Fully functional  

⚠️ **Data Persistence:**
- Data exists only while backend is running
- Render free tier sleeps after 15 min → data resets
- First request after sleep takes ~30-60 seconds to wake up

---

## 💰 Cost: **100% FREE**

| Service | Cost | What You Get |
|---------|------|--------------|
| **Render** | Free | Backend API with 750 hours/month |
| **Vercel** | Free | Frontend hosting, 100 GB bandwidth |
| **Database** | Free | In-memory (no external DB needed) |

**Total: $0/month** 🎉

---

## 🔄 Want Real Persistence Later?

### Upgrade to MongoDB Atlas:

1. **Create [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account** (free tier: 512 MB)
2. **Get connection string:**
   ```
   mongodb+srv://user:password@cluster.mongodb.net/traffic_management
   ```
3. **Update Render environment:**
   ```
   USE_MOCK_DB = false
   MONGODB_URL = mongodb+srv://user:password@cluster.mongodb.net/traffic_management
   ```
4. **Save** → Backend redeploys with real database

Now your data persists forever! See full `DEPLOYMENT.md` for detailed MongoDB setup.

---

## 🐛 Troubleshooting

### Backend Won't Start
- Check Render logs for errors
- Verify `USE_MOCK_DB=true` is set
- Ensure all environment variables are set

### Frontend Can't Connect
- Check CORS settings in Render
- Verify `VITE_API_URL` is correct in Vercel
- Check browser console for errors

### Slow First Load
- Render free tier sleeps after 15 min
- First request takes 30-60 seconds to wake up
- This is normal for free tier

### YOLO Model Issues
- Model auto-downloads on first start (~6 MB)
- May take 2-3 minutes on initial deploy
- Check Render logs for download progress

---

## 📝 Commands Quick Reference

### Test Backend Locally (Mock Mode)
```bash
cd minor_real/backend
echo "USE_MOCK_DB=true" >> .env
python -m uvicorn app.main:app --reload
```

### Test Frontend Locally
```bash
cd minor_real/frontend
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

### Deploy Backend Updates
```bash
git add .
git commit -m "Update backend"
git push origin master
# Render auto-deploys
```

### Deploy Frontend Updates
```bash
git add .
git commit -m "Update frontend"
git push origin master
# Vercel auto-deploys
```

---

## 🎓 Perfect for Your Project Presentation!

**Tell your evaluators:**

> "I've deployed a fully functional demo on Render and Vercel (both free tiers) without requiring an external database. The system uses an in-memory database for testing, making it easy to demonstrate all features. For production use, I can easily switch to MongoDB Atlas for persistent storage."

**Then show them:**
1. ✅ Live deployed URL
2. ✅ API documentation at `/docs`
3. ✅ Upload and process a video
4. ✅ View real-time vehicle detection
5. ✅ Check analytics and reports

---

## 🚀 Deploy Now!

**Total Time: ~10 minutes**

1. Deploy backend to Render (5 min)
2. Deploy frontend to Vercel (3 min)
3. Update CORS (2 min)

**Commands:**
```bash
# Frontend deploy
cd minor_real/frontend
vercel --prod

# Note your URLs and update CORS in Render dashboard
```

That's it! Your Smart Traffic Management System is live! 🎉
