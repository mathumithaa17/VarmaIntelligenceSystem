/**
 * Maps Backend Varma Names (from JSON data) to Unity Object Names (from User List).
 * This ensures exact matching in the 3D Model.
 */

export const mapBackendToUnityName = (backendName) => {
    if (!backendName) return "";

    const name = backendName.toLowerCase().trim();

    // 1. Explicit Mappings for tricky cases or mismatches
    const mappings = {
        // Backend "Sevikuttri_Kaalam" -> Unity "Sevikutri"
        "sevikuttri kaalam": "Sevikutri",
        "sevikuttri": "Sevikutri",

        // Backend "Pitthukai_Varmam" -> Unity "Pitthukai" (or Fix Pithukai if needed)
        "pitthukai varmam": "Pitthukai",
        "pitthukai": "Pitthukai",

        // Backend "Kaikatti_Kaalam"
        "kaikatti kaalam": "Kaikatti",
        "kaikatti": "Kaikatti",

        // Backend "Chippi_Varmam"
        "chippi varmam": "Chippi",
        "chippi": "Chippi",

        // Backend "Kakkattai_Kaalam"
        "kakkattai kaalam": "Kakkattai",
        "kakkattai": "Kakkattai",

        // Backend "Kachai_Varmam"
        "kachai varmam": "Kachai",
        "kachai": "Kachai",

        // Backend "Ani_Varmam"
        "ani varmam": "Ani",
        "ani": "Ani",

        // Backend "Visha_Manibantha_Varmam"
        "visha manibantha varmam": "VishaManibantha",
        "visha manibantha": "VishaManibantha",

        // Backend "Manibantha_Varmam"
        "manibantha varmam": "Manibantha",
        "manibantha": "Manibantha",
    };

    // Check explicit map first
    if (mappings[name]) {
        return mappings[name];
    }

    // 2. Default Normalization: Remove "Varmam", "Kaalam"
    // e.g. "Aasan Kaalam" -> "Aasan"
    let cleanName = backendName.replace(/_/g, " "); // "Aasan_Kaalam" -> "Aasan Kaalam"
    cleanName = cleanName.replace(/(Varmam|Kaalam|Kalam|varmam|kaalam|kalam)/gi, "").trim();

    // Remove numbers if any (though backend usually doesn't have them)
    return cleanName;
};
