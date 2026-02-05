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
        if (bestTransform != null)
        {
            if (!isSearchActive) HandleGlow(bestTransform.name);
            DisplayPointName(bestTransform.name, bestTransform);
        }
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
                if (targets.Contains(objNorm)) match = true;
                else
                {
                    foreach (string t in targets)
                    {
                        if (objNorm.Contains(t) || t.Contains(objNorm)) 
                        {
                            match = true;
                            if (t.Length < 3 || objNorm.Length < 3) match = false; 
                            break;
                        }
                    }
                }

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
        ClearGlow();
        string json = "{\"points\":[\"" + name + "\"]}";
        HighlightPointsList(json);
    }

    public void ClearGlow()
    {
        foreach (var v in activeGlow) if (v) v.SetGlow(false);
        activeGlow.Clear();
        // Do NOT reset isSearchActive here blindly, because HandleGlow calls this too.
        // But HandleGlow is for single click (which IS normal mode), or Search calls it?
        // Wait, HandleGlow sets single point. 
        // If HandleGlow is called, it means we are in Normal Mode (checked by caller).
        // Or if we call HandleGlow programmatically?
        // Let's stick to resetting it in ClearAllHighlights primarily.
        // However, if HandleGlow calls ClearGlow, the state remains whatever it was. 
        // If we are in Search Mode, we DON'T call HandleGlow.
        // If we are in Normal Mode, we CALL HandleGlow -> ClearGlow.
        // Ideally ClearGlow represents 'clearing' state.
        // Let's rely on ClearAllHighlights (explicit clear) to reset to Normal Mode.
        // And also, if manual single-click happens (Normal Mode), we are fine.
    }

    string NormalizeName(string raw)
    {
        if (string.IsNullOrEmpty(raw)) return "";
        string s = raw.ToLower();
        s = s.Replace("_l", "").Replace("_r", "");
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
