using UnityEngine;
using System.Collections.Generic;

public class VarmaPointHighlighter : MonoBehaviour
{
    // Dictionary to hold references to all Varma points by name
    private Dictionary<string, GameObject> varmaPoints = new Dictionary<string, GameObject>();

    public Material highlightMaterial; // Assign a glowing material in Inspector
    public Material defaultMaterial;   // Assign default material in Inspector

    void Start()
    {
        // automatically find all varma points if they are tagged or named specifically
        // Assuming Varma points are children of a specific object or tagged "VarmaPoint"
        GameObject[] points = GameObject.FindGameObjectsWithTag("VarmaPoint");
        foreach (GameObject p in points)
        {
            if (!varmaPoints.ContainsKey(p.name))
            {
                varmaPoints.Add(p.name, p);
            }
        }
    }

    // Helper class for JSON parsing arrays
    [System.Serializable]
    public class PointList
    {
        public string[] points;
    }

    // Called from React: "HighlightPoint"
    public void HighlightPoint(string pointName)
    {
        if (varmaPoints.ContainsKey(pointName))
        {
            GameObject point = varmaPoints[pointName];
            Renderer r = point.GetComponent<Renderer>();
            if (r != null)
            {
                r.material = highlightMaterial;
            }
        }
        else
        {
            Debug.LogWarning("Varma Point not found: " + pointName);
        }
    }

    // Called from React: "HighlightPointsList" - JSON payload: { "points": ["name1", "name2"] }
    public void HighlightPointsList(string jsonList)
    {
        try
        {
            PointList list = JsonUtility.FromJson<PointList>(jsonList);
            if (list == null || list.points == null) return;

            HashSet<string> activePoints = new HashSet<string>(list.points);

            foreach (var kvp in varmaPoints)
            {
                Renderer r = kvp.Value.GetComponent<Renderer>();
                if (r != null)
                {
                    // Check if this point name is in our list (case-insensitive if needed, but dict is usually strict)
                    // You might want to normalize names here if needed.
                    if (activePoints.Contains(kvp.Key))
                    {
                        r.material = highlightMaterial;
                    }
                    else
                    {
                        r.material = defaultMaterial;
                    }
                }
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError("Error parsing point list: " + e.Message);
        }
    }

    // Called from React: "ClearAllHighlights"
    public void ClearAllHighlights(string unused)
    {
        foreach (var kvp in varmaPoints)
        {
            Renderer r = kvp.Value.GetComponent<Renderer>();
            if (r != null)
            {
                r.material = defaultMaterial;
            }
        }
    }
    
    // Called from React: "SelectPoint"
    public void SelectPoint(string pointName)
    {
        // Don't clear others, just highlight this one (or handle differently)
        HighlightPoint(pointName);
    }
}
