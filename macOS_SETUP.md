# Varma Intelligence System - macOS Setup Guide

## The 404 Error - Root Cause & Fix

**Problem**: You were getting a 404 error when requesting `/Web_text/Build/buildFolder.loader.js`

**Root Cause**: The build files exist, but the asset server (Terminal 3) wasn't running when the application tried to load the Unity model.

**Solution Implemented**: 
1. Updated [unity_wrapper.html](varma-intelligence-system/public/unity_wrapper.html) with retry logic and better error handling
2. Created the missing `StreamingAssets` directory
3. Improved error messages to guide you

## How to Run the Application (Correct Order)

You need **4 terminals running simultaneously** in this specific order:

### Terminal 1: Backend Search Engine
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem
python backend/app.py
```
**Wait for**: "Retriever initialized successfully!"

### Terminal 2: RAG Service (Chatbot)
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem
python backend/rag_service.py
```
**Wait for**: "Service running at: http://localhost:5004"

### Terminal 3: Asset Server (MUST START BEFORE TERMINAL 4)
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
npx serve -s public -p 3001 --cors
```
**Wait for**: You should see a message showing the server is running on port 3001

### Terminal 4: Frontend Application
```bash
cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
npm start
```
This opens the application on http://localhost:3000

## Important Notes

1. **Terminal 3 MUST run before Terminal 4**: The asset server must be running before you load the frontend, otherwise the 3D model won't load.

2. **The improved unity_wrapper.html** now:
   - Retries loading the asset server up to 10 times (with 1-second delays)
   - Shows better status messages
   - Handles missing `createUnityInstance` gracefully
   - Has better error reporting if something goes wrong

3. **StreamingAssets directory** was created at `/varma-intelligence-system/public/Web_text/StreamingAssets/` (it was missing before)

4. **Ensure all build files exist**:
   - buildFolder.data
   - buildFolder.framework.js
   - buildFolder.loader.js
   - buildFolder.wasm

## If You Still Get Errors

1. **Check browser console** (F12) for detailed error messages
2. **Verify all 4 terminals are running** without errors
3. **Check ports are available**:
   - Backend: 5003
   - RAG Service: 5004
   - Frontend: 3000
   - Asset Server: 3001

4. **If Terminal 3 fails to start**:
   ```bash
   # Install serve globally if not already installed
   npm install -g serve
   
   # Then try again
   npx serve -s public -p 3001 --cors
   ```

5. **Hard refresh your browser** (Cmd+Shift+R on macOS) to clear cache

## File Changes Made

- [unity_wrapper.html](varma-intelligence-system/public/unity_wrapper.html) - Complete rewrite with retry logic and error handling
- Created: `varma-intelligence-system/public/Web_text/StreamingAssets/` directory

## Testing the Asset Server

To verify the asset server is serving files correctly:

```bash
# In a separate terminal
curl -I http://localhost:3001/Web_text/Build/buildFolder.loader.js

# You should see: "HTTP/1.1 200 OK"
# NOT "HTTP/1.1 404"
```

## Troubleshooting Cross-Platform Issues

This project uses absolute paths and localhost URLs. macOS should handle this fine, but:

- Ensure you're not behind a proxy
- Check firewall isn't blocking ports 3000-3004
- Verify Node.js is installed: `node --version`
- Verify Python is installed: `python3 --version`
