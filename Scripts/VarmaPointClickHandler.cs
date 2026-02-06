using UnityEngine;
using TMPro;
using System.Collections.Generic;

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

    private float hideTimer;
    private bool isDisplaying;
    private Vector2 mouseDownPosition;
    private int varmaLayerMask;
    private bool isSearchActive = false; // New flag to track search mode

    // 🔹 Already-existing glow support
    private static List<VarmaPointVisual> activeGlow = new();

    void Start()
    {
        Debug.Log("VarmaPointClickHandler START");

        if (!mainCamera)
            mainCamera = Camera.main;

        varmaLayerMask = LayerMask.GetMask("VarmaPoint");

        if (!infoPanel)
            Debug.LogError("InfoPanel not assigned!");
        else
            infoPanel.gameObject.SetActive(false);

        if (!displayText)
            Debug.LogError("DisplayText not assigned!");
        else
            displayText.gameObject.SetActive(false);

        if (!humanRotate)
            Debug.LogWarning("HumanRotate not assigned!");
    }

    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            mouseDownPosition = Input.mousePosition;
            if (humanRotate)
                humanRotate.allowRotation = false;
        }

        if (Input.GetMouseButtonUp(0))
        {
            float distance =
                Vector2.Distance(mouseDownPosition, Input.mousePosition);

            if (distance < dragThreshold)
                CheckForVarmaPointClick();

            if (humanRotate)
                humanRotate.allowRotation = true;
        }

        if (isDisplaying)
        {
            hideTimer -= Time.deltaTime;
            if (hideTimer <= 0f)
                HidePanel();
        }
    }

    void CheckForVarmaPointClick()
    {
        Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
        float sphereRadius = 0.25f;

        RaycastHit[] hits = Physics.SphereCastAll(
            ray,
            sphereRadius,
            200f,
            varmaLayerMask
        );

        if (hits.Length == 0)
            return;

        Vector2 mousePos = Input.mousePosition;
        float bestScreenDistance = float.MaxValue;
        Transform bestTransform = null;

        foreach (RaycastHit hit in hits)
        {
            Vector3 screenPos =
                mainCamera.WorldToScreenPoint(hit.transform.position);

            float screenDistance =
                Vector2.Distance(mousePos, screenPos);

            if (screenDistance < bestScreenDistance)
            {
                bestScreenDistance = screenDistance;
                bestTransform = hit.transform;
            }
        }

        if (bestTransform != null)
        {
        if (bestTransform != null)
        {
            if (!isSearchActive)
            {
                HandleGlow(bestTransform.name);
            }
            DisplayPointName(bestTransform.name, bestTransform);
        }
            DisplayPointName(bestTransform.name, bestTransform);
        }
    }

    void DisplayPointName(string pointName, Transform pointTransform)
    {
        if (!infoPanel || !displayText || !mainCamera)
            return;

        // ✅ ONLY CHANGE: clean name before display
        displayText.text = CleanVarmaName(pointName);
        displayText.gameObject.SetActive(true);

        Vector2 screenPos =
            mainCamera.WorldToScreenPoint(pointTransform.position);

        RectTransform canvasRect =
            infoPanel.parent as RectTransform;

        Vector2 localPoint;
        RectTransformUtility.ScreenPointToLocalPointInRectangle(
            canvasRect,
            screenPos,
            null,
            out localPoint
        );

        infoPanel.anchoredPosition =
            localPoint + screenOffset;

        infoPanel.gameObject.SetActive(true);

        isDisplaying = true;
        hideTimer = displayDuration;
    }

        hideTimer = displayDuration;
    }

    // Bridge method called by Web
    public void ClearAllHighlights(string ignore)
    {
        ClearGlow();
    }

    void HidePanel()
    {
        if (!infoPanel) return;

        infoPanel.gameObject.SetActive(false);

        if (displayText)
            displayText.gameObject.SetActive(false);

        isDisplaying = false;
    }

    // ================= ADDITIONAL CONCEPT (SAFE) =================

    void HandleGlow(string clickedName)
    {
        ClearGlow();

        string baseName = GetBaseName(clickedName);

        foreach (GameObject obj in GameObject.FindGameObjectsWithTag("VarmaPoint"))
        {
            if (GetBaseName(obj.name) == baseName)
            {
                VarmaPointVisual visual = obj.GetComponent<VarmaPointVisual>();
                if (visual != null)
                {
                    visual.SetGlow(true);
                    activeGlow.Add(visual);
                }
            }
        }
    }

    void ClearGlow()
    {
        foreach (var v in activeGlow)
            if (v != null)
                v.SetGlow(false);

        activeGlow.Clear();
        isSearchActive = false; // Reset whenever we clear explicitly or via HandleGlow
    }

    string GetBaseName(string name)
    {
        return name.Replace("_L", "").Replace("_R", "");
    }

    // 🔥 NEW CONCEPT (DISPLAY-ONLY CLEANING)
    string CleanVarmaName(string rawName)
    {
        string name = rawName.Replace("_L", "").Replace("_R", "");

        int underscoreIndex = name.IndexOf('_');
        if (underscoreIndex >= 0)
            name = name.Substring(underscoreIndex + 1);

        return name;
    }

    // ================= BRIDGE METHODS =================

    [System.Serializable]
    public class PointList
    {
        public string[] points;
    }

    public void HighlightPointsList(string jsonList)
    {
        try
        {
            // 1. Clear existing
            ClearGlow();

            // 2. Parse payload
            PointList list = JsonUtility.FromJson<PointList>(jsonList);
            if (list == null || list.points == null) return;

            // 3. Prepare normalized set
            HashSet<string> targetKeys = new HashSet<string>();
            foreach (string p in list.points)
            {
                targetKeys.Add(NormalizeForMatch(p));
            }

            // 4. Iterate all points
            int count = 0;
            foreach (GameObject obj in GameObject.FindGameObjectsWithTag("VarmaPoint"))
            {
                // Unpack the Unity name: "12_AasanKaalam" -> "aasan"
                string objKey = NormalizeForMatch(obj.name);
                
                // Check match
                bool match = false;
                
                // Direct match
                if (targetKeys.Contains(objKey)) match = true;

                // Substring fallback (for safety)
                if (!match)
                {
                    foreach (string t in targetKeys)
                    {
                        // Logic: if "kaikatti" is target, and obj is "kaikattikalam", it matches
                        // But since we stripped kalam, both should be "kaikatti".
                        // This fallback is for weird edge cases.
                        if (objKey.Contains(t) || t.Contains(objKey))
                        {
                            match = true;
                            break;
                        }
                    }
                }

                if (match)
                {
                    VarmaPointVisual visual = obj.GetComponent<VarmaPointVisual>();
                    if (visual != null)
                    {
                        visual.SetGlow(true);
                        activeGlow.Add(visual);
                        count++;
                    }
                }
            }

            if (count > 0)
            {
                isSearchActive = true; 
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError("Error in HighlightPointsList: " + e.Message);
        }
    }

    // 🔹 NORMALIZATION HELPER (The Secret Sauce)
    // Converts "12_AasanKaalam" -> "aasan"
    // Converts "Aasan Kalam" -> "aasan"
    string NormalizeForMatch(string raw)
    {
        if (string.IsNullOrEmpty(raw)) return "";

        string s = raw.ToLower();

        // 1. Remove standard suffixes/synonyms FIRST to avoid "Kalam" being treated as letters
        s = s.Replace("kaalam", "");
        s = s.Replace("kalam", "");
        s = s.Replace("varmam", "");
        s = s.Replace("varmum", "");

        // 2. Remove directional tags
        s = s.Replace("_l", "");
        s = s.Replace("_r", "");
        
        // 3. Keep ONLY LETTERS (so "12_" is gone)
        string letters = "";
        foreach(char c in s)
        {
            if (char.IsLetter(c)) letters += c;
        }

        return letters;
    }
}
