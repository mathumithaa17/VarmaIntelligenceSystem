using UnityEngine;
using System.Collections.Generic;

public class VarmaDatabase : MonoBehaviour
{
    public TextAsset varmaJson;   // varma_data.json

    public static Dictionary<string, VarmaData> Lookup;

    void Awake()
    {
        Lookup = new Dictionary<string, VarmaData>();

        if (!varmaJson)
        {
            Debug.LogError("Varma JSON not assigned!");
            return;
        }

        VarmaDataWrapper wrapper =
            JsonUtility.FromJson<VarmaDataWrapper>(varmaJson.text);

        foreach (var v in wrapper.varmas)
        {
            Lookup[v.varmaName] = v;
        }

        Debug.Log("Varma database loaded: " + Lookup.Count);
    }
}

