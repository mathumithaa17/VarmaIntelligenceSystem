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

    // 🔹 already-existing glow support
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
            HandleGlow(bestTransform.name);
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

            // 3. Prepare set for fast lookup (normalize input names if needed, assume they match base names)
            HashSet<string> targetNames = new HashSet<string>();
            foreach (string p in list.points)
            {
                // Ensure we compare apples to apples. 
                // The frontend likely sends "Thilartha Kalam", "Uchi Varma".
                // Our Unity objects might be "Varma_Thilartha Kalam_L".
                // GetBaseName handles the suffix, but we might need to handle the prefix too if GetBaseName doesn't.
                // Looking at GetBaseName implementation: it only removes _L and _R.
                // Looking at CleanVarmaName: it removes prefix before first _.
                // Let's rely on flexible matching or just direct contains.
                // For now, let's assume the input IS the base name or close to it.
                targetNames.Add(p.ToLower().Trim()); 
            }

            // 4. Iterate all points
            foreach (GameObject obj in GameObject.FindGameObjectsWithTag("VarmaPoint"))
            {
                // We need to extract the "meaningful" name from the object name
                // e.g. "01_Thilartha Kalam_L" -> "thilartha kalam"
                string objName = obj.name;
                
                // Use CleanVarmaName logic to get the pure name for comparison
                string cleanName = CleanVarmaName(objName).ToLower().Trim();
                
                // Check if this clean name is in our target list
                // OR checks if the target list has a name that is contained in the object name
                bool match = false;
                if (targetNames.Contains(cleanName)) match = true;
                
                // Fallback: check if any target is a substring of obj name
                if (!match)
                {
                    foreach(string t in targetNames)
                    {
                        if (cleanName.Contains(t) || t.Contains(cleanName))
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
                    }
                }
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError("Error in HighlightPointsList: " + e.Message);
        }
    }
}
