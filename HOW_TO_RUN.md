# How to Run the Varma Intelligence System

This guide explains how to set up and run the complete system, which consists of **four parts** that must run simultaneously:
1.  **Main Backend** (Port 5003) - For Search.
2.  **RAG Service** (Port 5004) - For Chat.
3.  **Frontend** (Port 3000) - The User Interface.
4.  **3D Asset Server** (Port 3001) - For Unity Files.

---

## 1. Prerequisites (Install First)
*   **Node.js**: [Download Here](https://nodejs.org/) (Version 16+ recommended).
*   **Python**: [Download Here](https://www.python.org/) (Version 3.8+).
*   **Ollama**: [Download Here](https://ollama.com/download) (Required for the Chatbot).

---

## 2. Initial Setup (Do this once)

### Step A: Setup Backend
1.  Open a terminal in the root folder (`FYP-26`).
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    ```
3.  Activate it:
    *   Windows: `venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```

### Step B: Setup Frontend
1.  Open a terminal in `varma-intelligence-system`:
    ```bash
    cd varma-intelligence-system
    ```
2.  Install packages:
    ```bash
    npm install
    ```

### Step C: Setup AI Model
1.  Open any terminal.
2.  Run the verification script provided:
    ```bash
    check_ollama.bat
    ```
3.  Or manually Install the model:
    ```bash
    ollama pull llama3
    ```

---

## 3. Running the Application (Every Time)

To run the system, you need **4 separate terminals**.

### Terminal 1: Main Backend (Search Engine)
```bash
# In root folder (FYP-26)
python backend/app.py
```
*Wait until you see: "Retriever initialized successfully!"*

### Terminal 2: RAG Service (Chatbot)
```bash
# In root folder (FYP-26)
python backend/rag_service.py
```
*Wait until you see: "Service running at: http://localhost:5004"*

### Terminal 3: 3D Asset Server
```bash
# In frontend folder (varma-intelligence-system)
cd varma-intelligence-system
npx serve -s public -p 3001 --cors
```

### Terminal 4: Frontend Application
```bash
# In frontend folder (varma-intelligence-system)
cd varma-intelligence-system
npm start
```

---

## 4. Accessing the App
*   Open your browser to: **http://localhost:3000**
*   **Symptom Search tab**: Uses Backend (5003) + 3D Server (3001).
*   **Ask Question tab**: Uses RAG Service (5004) + Ollama.

## Troubleshooting
*   **"Local LLM not installed"**: Ensure you installed Ollama and restarted your terminals. Run `check_ollama.bat`.
*   **500 Error**: Check the terminal output of the respective backend service.
*   **3D Model not loading**: Ensure Terminal 3 is running and serving port 3001.
