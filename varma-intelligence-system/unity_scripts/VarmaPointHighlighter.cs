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
            // Optional: Move camera to look at point?
        }
        else
        {
            Debug.LogWarning("Varma Point not found: " + pointName);
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
        HighlightPoint(pointName);
        // Add zoom logic here if needed
    }
}
