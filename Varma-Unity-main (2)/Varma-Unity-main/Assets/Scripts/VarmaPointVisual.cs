using UnityEngine;

public class VarmaPointVisual : MonoBehaviour
{
    public Material normalMat;
    public Material glowMat;

    private Renderer rend;

    // 🔹 ADDITION (pulse support)
    private bool isGlowing;
    private Color baseEmissionColor;

    void Awake()
    {
        rend = GetComponent<Renderer>();

        if (rend && normalMat)
            rend.material = normalMat;

        // 🔹 ADDITION: cache emission color safely
        if (glowMat != null && glowMat.HasProperty("_EmissionColor"))
        {
            baseEmissionColor = glowMat.GetColor("_EmissionColor");
        }
    }

    public void SetGlow(bool glow)
    {
        if (!rend) return;

        rend.material = glow ? glowMat : normalMat;

        // 🔹 ADDITION
        isGlowing = glow;

        // Reset emission when glow is turned off
        if (!glow && glowMat != null && glowMat.HasProperty("_EmissionColor"))
        {
            glowMat.SetColor("_EmissionColor", baseEmissionColor);
        }
    }

    // 🔹 ADDITION: smooth pulse animation
    void Update()
    {
        if (!isGlowing || glowMat == null) return;

        if (!glowMat.HasProperty("_EmissionColor")) return;

        float pulse = Mathf.Abs(Mathf.Sin(Time.time * 3f)); // speed
        float intensity = 1.5f + pulse * 1.5f;

        glowMat.SetColor("_EmissionColor", baseEmissionColor * intensity);
    }
}
