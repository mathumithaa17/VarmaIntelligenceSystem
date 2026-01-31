# Troubleshooting Guide - Varma Intelligence System

## Common Issues and Solutions

### Issue 1: Still Getting 404 Errors

**Symptoms**: 
- Browser console shows: "Returned 404" for buildFolder.loader.js
- 3D model doesn't load, spinner keeps spinning

**Solutions**:
1. **Check Terminal 3 is running**
   ```bash
   # In Terminal 3, you should see:
   # "Accepting connections at http://localhost:3001"
   ```
   
2. **Kill and restart all servers**
   ```bash
   # Terminal 1
   Ctrl+C to stop python backend/app.py
   python backend/app.py
   
   # Terminal 2
   Ctrl+C to stop python backend/rag_service.py
   python backend/rag_service.py
   
   # Terminal 3 - START THIS FIRST
   Ctrl+C to stop serve
   npx serve -s public -p 3001 --cors
   # Wait 2-3 seconds for server to start
   
   # Terminal 4 - ONLY AFTER TERMINAL 3 IS RUNNING
   Ctrl+C to stop npm start
   npm start
   ```

3. **Verify port 3001 is accessible**
   ```bash
   # In a new terminal
   curl -I http://localhost:3001/Web_text/Build/buildFolder.loader.js
   
   # Should show: HTTP/1.1 200 OK
   # If not, the asset server isn't running properly
   ```

### Issue 2: "Failed to load 3D model" Message

**Symptoms**:
- Loading screen shows error after several retries
- Loader status shows: "Failed to load 3D model"

**Solutions**:
1. **Browser console troubleshooting** (Press F12)
   - Look for the actual error message
   - Copy the full error and search online
   
2. **Check the build files exist**
   ```bash
   ls -la /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system/public/Web_text/Build/
   
   # You should see:
   # -rw-r--r-- ... buildFolder.data
   # -rw-r--r-- ... buildFolder.framework.js
   # -rw-r--r-- ... buildFolder.loader.js
   # -rw-r--r-- ... buildFolder.wasm
   ```

3. **Check StreamingAssets directory exists**
   ```bash
   ls -la /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system/public/Web_text/StreamingAssets/
   
   # Directory should exist (can be empty)
   ```

### Issue 3: Port Already in Use

**Symptoms**:
- Error like "Port 3000 already in use" or "Port 3001 already in use"

**Solutions**:
1. **Find and kill process on port 3000**
   ```bash
   lsof -i :3000
   # Get the PID from output
   kill -9 <PID>
   ```

2. **Find and kill process on port 3001**
   ```bash
   lsof -i :3001
   # Get the PID from output
   kill -9 <PID>
   ```

3. **Find and kill process on port 5003 (Backend)**
   ```bash
   lsof -i :5003
   kill -9 <PID>
   ```

4. **Find and kill process on port 5004 (RAG Service)**
   ```bash
   lsof -i :5004
   kill -9 <PID>
   ```

### Issue 4: "npm start" Fails

**Symptoms**:
- Terminal 4 shows npm errors
- React development server won't start

**Solutions**:
1. **Clear npm cache**
   ```bash
   cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
   npm cache clean --force
   npm install
   npm start
   ```

2. **Check Node.js version**
   ```bash
   node --version
   # Should be v14 or higher
   ```

3. **Reinstall dependencies**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

### Issue 5: "npx serve" Command Not Found

**Symptoms**:
- Terminal 3 shows: "command not found: serve"

**Solutions**:
1. **Install serve globally**
   ```bash
   npm install -g serve
   ```

2. **Try using npx again**
   ```bash
   cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system
   npx serve -s public -p 3001 --cors
   ```

### Issue 6: Python Backend Won't Start

**Symptoms**:
- Terminal 1 or 2 shows Python errors
- Backend won't initialize

**Solutions**:
1. **Check Python version**
   ```bash
   python3 --version
   # Should be 3.8 - 3.11
   ```

2. **Check dependencies are installed**
   ```bash
   cd /Users/mathumithamathiyalagan/Desktop/fyp2/VarmaIntelligenceSystem
   pip install -r backend/requirements.txt
   ```

3. **Check Ollama is running** (needed for chatbot)
   ```bash
   # Ollama should be running as a service
   # Try pulling the model
   ollama pull llama3
   ```

### Issue 7: Browser Shows Blank Page

**Symptoms**:
- Application loads but shows nothing
- No error messages

**Solutions**:
1. **Hard refresh browser** (Cmd+Shift+R on macOS)

2. **Clear browser cache**
   - Press Cmd+Shift+Delete
   - Clear browsing data

3. **Check browser console for errors** (F12)
   - Look for red error messages
   - Screenshot and refer to this guide

### Issue 8: 3D Model Doesn't Respond to Clicks

**Symptoms**:
- Model loads and displays
- But clicking on it doesn't do anything

**Solutions**:
1. **Check browser console** for JavaScript errors

2. **Verify all 4 terminals are running**
   - Backend must be running (Terminal 1)
   - RAG Service must be running (Terminal 2)
   - Asset Server must be running (Terminal 3)
   - Frontend must be running (Terminal 4)

3. **Refresh the page** and try again

## Getting Help

If none of these solutions work:

1. **Check browser console** (F12) and screenshot error messages
2. **Check Terminal outputs** for error messages
3. **Verify file structure** matches what's shown in this project
4. **Make sure all prerequisites are installed**:
   - Node.js v14+
   - Python 3.8-3.11
   - Ollama

## Quick Health Check

Run this to verify everything is set up:

```bash
# Check Node.js
node --version

# Check Python
python3 --version

# Check npm
npm --version

# Check if serve is available
npx serve --version

# Check if Ollama is running
curl -s http://localhost:11434/api/tags || echo "Ollama not running"

# List the build files
ls -la ~/Desktop/fyp2/VarmaIntelligenceSystem/varma-intelligence-system/public/Web_text/Build/
```

All checks should show output without errors.
