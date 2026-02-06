using UnityEngine;
using TMPro;
using System.Collections.Generic;
using System.Linq;

public class VarmaPointClickHandler : MonoBehaviour
{
    [Header("UI (Screen Space)")]
    public RectTransform infoPanel;
    public TextMeshProUGUI displayText;
    public Vector2 screenOffset = new Vector2(20f, 20f);

    [Header("Camera")]
    public Camera mainCamera;

    [Header("Rotation Control")]
    public HumanRotate humanRotate;

    [Header("Settings")]
    public float displayDuration = 3f;
    public float dragThreshold = 15f;
    public bool debugMode = true;

    private float hideTimer;
    private bool isDisplaying;
    private Vector2 mouseDownPosition;
    private int varmaLayerMask;
    private bool isSearchActive = false;

    private static List<VarmaPointVisual> activeGlow = new List<VarmaPointVisual>();

    // ================= AUTO-FIX & SETUP =================
    void Awake()
    {
        // 1. AUTO-RENAME: Ensure this object is named correctly for the browser to find it
        if (gameObject.name != "VarmaManager")
        {
            Debug.Log($"[VarmaManager] Auto-Renaming '{gameObject.name}' to 'VarmaManager' for browser compatibility.");
            gameObject.name = "VarmaManager";
        }
    }

    void Start()
    {
        Debug.Log("[VarmaManager] STARTING v2.1 (Deprecation Fixes)...");

        if (!mainCamera) mainCamera = Camera.main;

        // Layer Setup
        int layerIndex = LayerMask.NameToLayer("VarmaPoint");
        varmaLayerMask = (layerIndex != -1) ? (1 << layerIndex) : Physics.DefaultRaycastLayers;

        // Auto-find HumanRotate
        if (!humanRotate) humanRotate = FindFirstObjectByType<HumanRotate>();
        
        // Disable UI initially
        if (infoPanel) infoPanel.gameObject.SetActive(false);
        if (displayText) displayText.gameObject.SetActive(false);

        // SELF-DIAGNOSTIC
        GameObject[] tagged = GameObject.FindGameObjectsWithTag("VarmaPoint");
        Debug.Log($"[VarmaManager] Initial check: Found {tagged.Length} objects tagged 'VarmaPoint'.");
    }

    // ================= INTERACTION =================
    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            mouseDownPosition = Input.mousePosition;
            if (humanRotate) humanRotate.allowRotation = false;
        }

        if (Input.GetMouseButtonUp(0))
        {
            float d = Vector2.Distance(mouseDownPosition, Input.mousePosition);
            if (d < dragThreshold) CheckForVarmaPointClick();
            if (humanRotate) humanRotate.allowRotation = true;
        }

        if (isDisplaying)
        {
            hideTimer -= Time.deltaTime;
            if (hideTimer <= 0f) HidePanel();
        }
    }

    void CheckForVarmaPointClick()
    {
        Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
        RaycastHit[] hits = Physics.SphereCastAll(ray, 0.25f, 200f, varmaLayerMask);

        if (hits.Length == 0) return;

        Transform bestTransform = null;
        float bestDist = float.MaxValue;

        foreach (RaycastHit hit in hits)
        {
            if (varmaLayerMask != Physics.DefaultRaycastLayers && !hit.transform.CompareTag("VarmaPoint")) 
                continue;

            float d = Vector2.Distance(Input.mousePosition, mainCamera.WorldToScreenPoint(hit.transform.position));
            if (d < bestDist)
            {
                bestDist = d;
                bestTransform = hit.transform;
            }
        }

        if (bestTransform != null)
        {
            if (!isSearchActive) HandleGlow(bestTransform.name);
            DisplayPointName(bestTransform.name, bestTransform);
        }
    }

    void HidePanel()
    {
        if (infoPanel) infoPanel.gameObject.SetActive(false);
        if (displayText) displayText.gameObject.SetActive(false);
        isDisplaying = false;
    }

    // ================= HIGHLIGHTING LOGIC (ROBUST) =================

    [System.Serializable]
    public class PointList { public string[] points; }

    public void HighlightPointsList(string jsonList)
    {
        Debug.Log($"[VarmaManager] MSG RECEIVED: {jsonList}");
        try
        {
            ClearGlow();
            PointList list = JsonUtility.FromJson<PointList>(jsonList);
            if (list == null || list.points == null) return;

            HashSet<string> targets = new HashSet<string>();
            foreach (string p in list.points) targets.Add(NormalizeName(p));

            List<GameObject> candidates = new List<GameObject>(GameObject.FindGameObjectsWithTag("VarmaPoint"));
            
            // FALLBACK: If few/no tags, search ALL renderers
            if (candidates.Count < 5) 
            {
                Debug.LogWarning("[VarmaManager] Few tags found. Scanning ALL objects with Renderers (Fallback Mode).");
                Renderer[] allRenderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);
                foreach(var r in allRenderers) candidates.Add(r.gameObject);
            }

            int count = 0;
            foreach (GameObject obj in candidates)
            {
                string objNorm = NormalizeName(obj.name);

                bool match = false;
                if (targets.Contains(objNorm)) 
                {
                    match = true;
                }
                
                // 🛑 REMOVED Substring logic to prevent overlaps (e.g. VishaManibantha vs Manibantha)
                // With the new robust normalization, Exact Match is sufficient and safer.

                if (match)
                {
                    VarmaPointVisual visual = obj.GetComponent<VarmaPointVisual>();
                    if (visual == null) visual = obj.AddComponent<VarmaPointVisual>();
                    
                    visual.SetGlow(true);
                    activeGlow.Add(visual);
                    count++;
                }
            }
            Debug.Log($"[VarmaManager] Highlighted {count} points.");
            if (count > 0) isSearchActive = true;
        }
        catch (System.Exception e) { Debug.LogError($"[VarmaManager] Error: {e.Message}"); }
    }

    public void ClearAllHighlights(string ignore) 
    {
        ClearGlow();
        isSearchActive = false;
    }

    void HandleGlow(string name)
    {
        // 1. Reset everything first
        ClearGlow();
        isSearchActive = false;

        // 2. Find and Highlight just this one point
        Debug.Log($"[VarmaManager] HandleGlow: Highlighting single point '{name}'");
        
        GameObject target = GameObject.Find(name);
        if (target != null)
        {
            VarmaPointVisual visual = target.GetComponent<VarmaPointVisual>();
            if (visual == null) visual = target.AddComponent<VarmaPointVisual>();

            visual.SetGlow(true);
            activeGlow.Add(visual);
        }
        else
        {
            Debug.LogWarning($"[VarmaManager] Could not find object with name '{name}' to highlight.");
        }

        // 3. Explicitly ensure Search Mode is OFF
        isSearchActive = false;
    }

    private void ClearAllHighlights_Internal()
    {
        ClearGlow();
        isSearchActive = false;
    }

    // Called from React via UnityModel3DViewer
    public void SelectPoint(string name)
    {
        Debug.Log($"[VarmaManager] SelectPoint called for: {name}");
        // Treat this as a manual selection? Or part of search?
        // If it comes from React "Symptom Search", it shouldn't clear search results.
        // But if we want to Highlight just this one...
        
        // Actually, React sends 'SelectPoint' when a card is clicked.
        // If we want to maintain search results, we should NOT call ClearAllHighlights_Internal here if search is active.
        
        // Let's defer to HandleGlow but WITHOUT forced reset if search is active?
        // Wait, HandleGlow forces reset.
        
        // BETTER LOGIC:
        if (isSearchActive)
        {
            // Just show the name, maybe pulse it? Don't clear others.
            // Find the transform and show name.
            Transform t = null;
            foreach(var g in activeGlow) 
            {
                if (NormalizeName(g.name) == NormalizeName(name)) 
                {
                    t = g.transform;
                    break;
                }
            }
            
            if (t == null)
            {
                 // Try to find it even if not highlighted
                 GameObject obj = GameObject.Find(name);
                 if (obj) t = obj.transform;
            }

            if (t) DisplayPointName(t.name, t);
        }
        else
        {
            // Manual selection behavior
            HandleGlow(name);
        }
    }

    public void ClearGlow()
    {
        Debug.Log($"[VarmaManager] ClearGlow called. Active glows count: {activeGlow.Count}");
        foreach (var v in activeGlow) if (v) v.SetGlow(false);
        activeGlow.Clear();
        // Ideally ClearGlow represents 'clearing' state.
        // Let's rely on ClearAllHighlights (explicit clear) to reset to Normal Mode.
        // And also, if manual single-click happens (Normal Mode), we are fine.
    }

    string NormalizeName(string raw)
    {
        if (string.IsNullOrEmpty(raw)) return "";
        string s = raw.ToLower().Trim();
        s = s.Replace(" ", ""); // Pre-strip spaces

        // 0. MANUAL FIXES (The "Alias Map")
        // Mapping: [Search Name] -> [Unity Name Base]
        // This solves "Sevikuttri" (DB) vs "Sevikutri" (Unity)
        if (s.Contains("sevikuttri")) s = s.Replace("sevikuttri", "sevikutri");
        if (s.Contains("pitthukai")) s = s.Replace("pitthukai", "pithukai"); // Variation check
        if (s.Contains("kachai")) s = s.Replace("kachai", "kachai"); // Ensure consistency
        
        // 1. Remove standard suffixes/synonyms
        s = s.Replace("kaalam", "");
        s = s.Replace("kalam", "");
        s = s.Replace("varmam", "");
        s = s.Replace("varmum", "");

        // 2. Remove directional tags
        s = s.Replace("_l", "");
        s = s.Replace("_r", "");
        
        // 3. Remove numbers (e.g. "12_") and special chars
        return new string(s.Where(char.IsLetter).ToArray());
    }

    void DisplayPointName(string name, Transform t)
    {
        if (!infoPanel || !displayText) return;
        displayText.text = name.Replace("_", " ");
        displayText.gameObject.SetActive(true);
        infoPanel.gameObject.SetActive(true);
        isDisplaying = true;
        hideTimer = displayDuration;
        
        Vector2 screenPos = mainCamera.WorldToScreenPoint(t.position);
        RectTransformUtility.ScreenPointToLocalPointInRectangle(infoPanel.parent as RectTransform, screenPos, null, out Vector2 local);
        infoPanel.anchoredPosition = local + screenOffset;
    }
}
