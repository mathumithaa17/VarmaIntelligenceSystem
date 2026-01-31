# QUICK REFERENCE - How to Run Your Application

## ⚡ The Problem You Had
404 Error: `GET /Web_text/Build/buildFolder.loader.js`

## ✅ What Was Fixed
1. Added retry logic to load the 3D model
2. Created missing StreamingAssets directory
3. Better error messages to help debugging
4. All build files verified in place

## 🚀 How to Start (4 Terminals, THIS ORDER)

### Terminal 1: Backend
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem
python backend/app.py
```
Wait for: "Retriever initialized successfully!"

### Terminal 2: Chat Service
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem
python backend/rag_service.py
```
Wait for: "Service running at: http://localhost:5004"

### Terminal 3: Asset Server ⭐ START THIS BEFORE TERMINAL 4
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
npx serve -s public -p 3001 --cors
```
Wait for: Server confirmation on port 3001

### Terminal 4: Frontend
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
npm start
```
Automatically opens http://localhost:3000

## 🔍 Verify Everything Works

```bash
# Test asset server in a new terminal
curl -I http://localhost:3001/Web_text/Build/buildFolder.loader.js

# Should show: HTTP/1.1 200 OK ✓
```

## 📋 Ports Used
- 3000: React Frontend
- 3001: Asset Server (3D Model)
- 5003: Backend Search
- 5004: RAG Chat Service

## ❓ Still Not Working?
1. Read TROUBLESHOOTING.md for detailed help
2. Check browser console (F12) for errors
3. Verify all 4 terminals running without errors
4. Hard refresh browser (Cmd+Shift+R)

## 📚 Documentation Added
- **FIX_SUMMARY.md** - What was wrong and fixed
- **macOS_SETUP.md** - Complete setup guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **QUICK_START.sh** - Reference script

---
You're all set! Your application should now work perfectly. 🎉
