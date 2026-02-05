# Important Code Snippets for Presentation

## Module 2: Unity Integration (3D Visualization)

### 1. React Component: Sending Data to Unity
**File:** `src/components/UnityModel3DViewer.jsx`

This snippet demonstrates how the React frontend sends highlighting commands to the Unity instance via the iframe.

```javascript
// Function to send messages to the Unity iframe
const sendToUnity = (type, payload) => {
  if (iframeRef.current && iframeRef.current.contentWindow) {
    console.log(`Sending to Unity [${type}]:`, payload);
    iframeRef.current.contentWindow.postMessage({ type, payload }, '*');
  }
};

// Hook to trigger highlighting when 'highlightedPoints' prop changes
useEffect(() => {
  if (iframeLoaded) {
    if (highlightedPoints.length > 0) {
      // Prepare list of names mapped from backend to Unity format
      const names = highlightedPoints.map(p => p.unity_name || p.name);
      const mappedNames = mapBackendToUnityNames(names);
      
      // Send JSON payload to Unity
      const jsonPayload = JSON.stringify({ points: mappedNames });
      sendToUnity('HighlightPointsList', jsonPayload);
    } else {
      sendToUnity('ClearAllHighlights', '');
    }
  }
}, [highlightedPoints, iframeLoaded]);
```

### 2. Unity Wrapper: Briding Web & Engine
**File:** `public/unity_wrapper.html`

This HTML file acts as the bridge, listening for messages from React and calling valid C# methods within the Unity instance.

```javascript
// Listen for messages from React
window.addEventListener('message', function (event) {
  if (!myUnityInstance) return;

  const data = event.data;
  
  // Helper to broadcast message to the correct Unity GameObject
  function sendToUnityObject(method, payload) {
    // Try multiple target names to ensure the message is received
    myUnityInstance.SendMessage('VarmaManager', method, payload);
    myUnityInstance.SendMessage('VarmaPointClickHandler', method, payload);
  }

  if (data.type === 'HighlightPointsList') {
    sendToUnityObject('HighlightPointsList', data.payload);
  } else if (data.type === 'ClearAllHighlights') {
    sendToUnityObject('ClearAllHighlights', '');
  }
});
```

### 3. Unity C# Script: Handling Visuals
**File:** `Assets/Scripts/VarmaPointClickHandler.cs`

This C# script runs inside the Unity engine. It parses the JSON list of points and applies a "glow" effect to the matching 3D objects.

```csharp
[System.Serializable]
public class PointList { public string[] points; }

public void HighlightPointsList(string jsonList)
{
    try
    {
        ClearGlow(); // Reset existing highlights
        PointList list = JsonUtility.FromJson<PointList>(jsonList);
        
        // Find and highlight all matching objects
        List<GameObject> candidates = new List<GameObject>(GameObject.FindGameObjectsWithTag("VarmaPoint"));
        
        foreach (GameObject obj in candidates)
        {
            // Check if object name matches one of the target points
            if (IsMatch(obj.name, list.points))
            {
                VarmaPointVisual visual = obj.GetComponent<VarmaPointVisual>();
                if (visual == null) visual = obj.AddComponent<VarmaPointVisual>();
                
                visual.SetGlow(true); // Enable visual highlight
                activeGlow.Add(visual);
            }
        }
    }
    catch (System.Exception e) { Debug.LogError($"Error: {e.Message}"); }
}
```

---

## Module 3: RAG (Retrieval Augmented Generation)

### 1. RAG Core Pipeline
**File:** `backend/rag_service.py`

This function represents the core RAG logic: Retrieve context -> Build Prompt -> Generate Answer.

```python
@app.route('/api/rag/query', methods=['POST'])
def rag_query():
    """RAG question answering endpoint"""
    data = request.get_json()
    question = data['question'].strip()
    
    # 1. Retrieve relevant documents (Semantic Search)
    # Returns a list of text chunks most relevant to the user's question
    docs = retriever.retrieve(question)
    
    # 2. Build Context
    # Concatenate retrieved chunks to form the background context
    context = "\n\n".join([d.get("text", "") for d in docs])
    
    # 3. Build Prompt
    # Combine system instructions, context, and user question
    prompt = build_prompt(question, context)
    
    # 4. Generate Answer
    # query the LLM (Large Language Model)
    response_text = generate(prompt)
    
    return jsonify({
        "answer": response_text,
        "sources": ["Varma Text Index"],
        "confidence": 1.0
    })
```

### 2. Symptom Search (Hybrid Retrieval)
**File:** `backend/app.py`

This snippet shows how the symptom search connects to the retrieval system, using parameters for both lexical (exact) and semantic (fuzzy) matching.

```python
@app.route('/api/symptom-search', methods=['POST'])
def symptom_search():
    data = request.get_json()
    symptom_query = data['query'].strip()
    
    # Call hybrid retrieval system
    # Balances keyword matching (lexical) with meaning-based matching (semantic)
    result = retriever.retrieve(
        query=symptom_query,
        top_symptoms=15,       # Number of similar symptoms to consider
        top_varmas=5,          # Number of Varma points to return
        lexical_threshold=0.45,
        semantic_threshold=0.55,
        verification_threshold=0.3
    )
    
    # Format and return the results for the UI
    response = format_for_ui(result, symptom_query, 0)
    return jsonify(response), 200
```
