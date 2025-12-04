# 🎥 How Multi-Camera System Works - Simple Guide

## 📋 Quick Answer

**Q: Do I need 4 cameras?**  
**A: NO! You can use 1, 2, 3, or 4 cameras. The system works perfectly with any number.**

---

## 🎯 How Camera Assignment Works

### **Scenario 1: You Have 1 Camera** ✅ (EASIEST - PERFECT FOR DEMO)

```
Your Setup:
- 1 camera (video file or phone camera)

What You'll See on Dashboard:
┌─────────────┬─────────────┐
│   NORTH ↑   │   SOUTH ↓   │
│  🎥 LIVE    │  ⚫ OFFLINE  │
│  (Your cam) │             │
├─────────────┼─────────────┤
│   EAST →    │   WEST ←    │
│  ⚫ OFFLINE  │  ⚫ OFFLINE  │
└─────────────┴─────────────┘

✅ Your camera appears in NORTH direction
✅ Other 3 show "Camera Offline" 
✅ System still calculates green time for North
✅ Perfect for demonstration!
```

**How to Control Direction:**
Just name your camera with direction keyword:

```
Camera Name: "North Junction" → Shows in NORTH
Camera Name: "South Camera" → Shows in SOUTH  
Camera Name: "East Road" → Shows in EAST
Camera Name: "West Highway" → Shows in WEST
Camera Name: "Main Camera" → Shows in NORTH (default)
```

---

### **Scenario 2: You Have 2 Cameras** ✅ (GREAT FOR COMPARISON)

```
Your Setup:
- Camera 1: Named "North Junction"
- Camera 2: Named "South Traffic"

What You'll See:
┌─────────────┬─────────────┐
│   NORTH ↑   │   SOUTH ↓   │
│  🎥 Camera1 │  🎥 Camera2 │
├─────────────┼─────────────┤
│   EAST →    │   WEST ←    │
│  ⚫ OFFLINE  │  ⚫ OFFLINE  │
└─────────────┴─────────────┘

✅ System compares North vs South traffic
✅ Green signal goes to busier direction
✅ Shows intelligent traffic management
```

---

### **Scenario 3: You Have 4 Cameras** ✅ (FULL INTERSECTION)

```
Your Setup:
- Camera 1: "North"
- Camera 2: "South"  
- Camera 3: "East"
- Camera 4: "West"

What You'll See:
┌─────────────┬─────────────┐
│   NORTH ↑   │   SOUTH ↓   │
│  🎥 Camera1 │  🎥 Camera2 │
├─────────────┼─────────────┤
│   EAST →    │   WEST ←    │
│  🎥 Camera3 │  🎥 Camera4 │
└─────────────┴─────────────┘

✅ Complete 4-way intersection
✅ System analyzes all 4 directions
✅ Optimal signal timing for all directions
```

---

## 🚀 Step-by-Step Demo Setup

### **Using Your Phone Camera (Recommended)**

1. **Install IP Webcam** on Android phone
2. **Start Server** → Note the IP (e.g., 192.168.29.92:8080)
3. **Go to Camera Management** in your app
4. **Click "Add Camera"**:
   - Camera ID: `cam_phone_1`
   - Camera Name: `North Junction` (or any direction you want)
   - URL: `http://192.168.29.92:8080/video`
   - Location: `Junction 01`
5. **Click "Start Stream"**
6. **Go to Dashboard** → Your live feed appears in NORTH direction!

---

### **Using Video File**

1. **Prepare a traffic video** (MP4 format recommended)
2. **Place video** in: `minor_real/data/videos/`
3. **Go to Camera Management**
4. **Click "Add Camera"**:
   - Camera ID: `cam_video_1`
   - Camera Name: `South Traffic` (choose any direction)
   - URL: `file:///C:/path/to/your/video.mp4`
   - Location: `Junction 01`
5. **Click "Start Stream"**
6. **Go to Dashboard** → Video plays in SOUTH direction!

---

## 💡 Smart Direction Assignment

The system automatically assigns directions based on camera name:

| Camera Name Contains | Shows in Direction |
|---------------------|-------------------|
| "North" or "N" | ⬆️ NORTH (Top-Left) |
| "South" or "S" | ⬇️ SOUTH (Top-Right) |
| "East" or "E" | ➡️ EAST (Bottom-Left) |
| "West" or "W" | ⬅️ WEST (Bottom-Right) |
| No keyword | ⬆️ NORTH (Default) |

**Examples:**
```
✅ "North Junction Camera" → NORTH
✅ "Junction-S" → SOUTH
✅ "Camera East Side" → EAST  
✅ "W-Highway" → WEST
✅ "Main Camera" → NORTH (default)
```

---

## 🎨 Visual Indicators

### **Camera Borders:**
- **🟢 Green Glowing Border** = This direction has green signal (active)
- **🔴 Red Pulsing Border** = Emergency vehicle detected!
- **⚫ Gray Border** = Red signal (waiting)
- **📷 "Camera Offline"** = No camera connected to this direction

### **Connection Status:**
- **"1/4 Active Cameras"** = You have 1 camera running
- **"2/4 Active Cameras"** = You have 2 cameras running
- **"4/4 Active Cameras"** = All 4 directions covered

---

## 🎬 Presentation Script

### **For 1 Camera Demo:**

> "This is our multi-camera intersection monitoring system. Currently, I have one camera active in the North direction - you can see the live feed here. The system is designed for 4-way intersections, but works perfectly with any number of cameras.
>
> Notice how the system is already calculating traffic metrics - vehicle count, congestion level, and recommended green time. With 15 vehicles detected, it's recommending 60 seconds of green time.
>
> If I had cameras in all 4 directions, the system would compare traffic density across all directions and automatically give priority to the busiest one. Emergency vehicles get immediate green signal override."

### **For 2 Camera Demo:**

> "Here we have two active cameras - North and South. Look at the traffic density: North has 20 vehicles with 80% congestion, while South has only 8 vehicles with 30% congestion.
>
> See the green glowing border on North? The system has intelligently given it the green signal because it has more traffic. North gets 70 seconds green time, while South will get the minimum 35 seconds when it's its turn.
>
> This is adaptive traffic management in action - signals change based on real-time traffic, not fixed timers."

---

## ❓ Common Questions

### **"Will it work with just 1 camera for the demo?"**
✅ **YES!** It looks great with 1 camera. The other 3 directions show "Offline" which actually demonstrates the system's scalability.

### **"Can I use my phone camera?"**
✅ **YES!** Use IP Webcam app. It works perfectly and shows real-time detection.

### **"Do I need 4 separate video files?"**
❌ **NO!** You can use the same video file 4 times with different camera names if needed. Or just use 1.

### **"How do I change which direction my camera appears in?"**
✅ Just edit the camera name to include "North", "South", "East", or "West"

### **"What if I don't specify direction in the name?"**
✅ It will automatically go to North (first available direction)

### **"Can I add more cameras later?"**
✅ **YES!** Add cameras anytime. Each new camera fills the next available direction.

### **"What if all 4 directions are filled and I add a 5th camera?"**
The 5th camera won't appear on the 4-way dashboard (it's designed for intersections with 4 directions max). But you can still manage it from Camera Management page.

---

## 🔧 Troubleshooting

### **"My camera shows offline on Dashboard"**
1. Check if stream is started in Camera Management
2. Verify camera URL is correct (use `http://` not `https://`)
3. Wait 5-10 seconds for connection
4. Check browser console for errors

### **"Camera appears in wrong direction"**
1. Go to Camera Management
2. Edit camera name to include desired direction
3. Stop and restart the stream
4. Check Dashboard again

### **"Video is laggy"**
This is normal - system processes every 3rd frame for performance. If too slow:
1. Reduce phone camera resolution (if using IP Webcam)
2. Use smaller video file
3. Close other applications

---

## 🎯 Quick Setup Checklist

For fastest demo setup:

- [ ] Backend running: `uvicorn app.main:app --reload`
- [ ] Frontend running: `npm run dev`
- [ ] Phone camera ready OR video file prepared
- [ ] Go to Camera Management
- [ ] Add 1 camera with name "North Junction"
- [ ] Click "Start Stream"
- [ ] Go to Dashboard
- [ ] See live feed in North direction! ✅

**You're ready to demo!** 🎉

---

## 📊 Demo Impact

**What judges will see:**
1. Professional 4-way intersection dashboard
2. Real-time vehicle detection
3. Intelligent signal timing
4. Works with 1 camera (shows scalability)
5. Emergency vehicle priority
6. Live congestion monitoring

**What they'll think:**
> "This team understands real-world deployment. Their system works with existing infrastructure and scales from 1 to 4 cameras seamlessly. The intelligent signal control is impressive!"

---

**Remember:** Having 1 camera is PERFECT for demo. It shows the system works while demonstrating it can scale to full 4-camera intersections! 🚀
