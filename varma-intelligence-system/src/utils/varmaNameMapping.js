
// Map of normalized backend names to Unity object base names
// We use a normalized key (lowercase, no underscores, no numbers) to match against backend data
const varmaMap = {
  "utchivarmam": ["1_UtchiVarmam"],
  "kondaikolli": ["2_KondaiKolli"],
  "seerungkolli": ["3_Seerungkolli"],
  "pidarivarmam": ["4_PidariVarmam"],
  "suruthivarmam": ["5_SuruthiVarmam"],
  "porchaivarmam": ["6_Porchai_L", "6_Porchai_R"],
  "suzhiyadivarmam": ["7_SuzhiyadiVarmam"],
  "kutrivarmam": ["8_KutriVarmam_L", "8_KutriVarmam_R"],
  "sevikuttrikaalam": ["9_Sevikutri_L", "9_Sevikutri_R"], // Spelling fix: Sevikuttri -> Sevikutri
  "poigaikaalam": ["10_PoigaiKaalam"],
  "chennivarmam": ["11_ChenniVarmam"],
  "aasankaalam": ["12_AasanKaalam"],
  "annankaalam": ["13_AnnanKaalam"],
  "peruchalvarmam": ["14_PeruchalVarmam"],
  "thilardhavarmam": ["15_ThilardhaVarmam"],
  "patchivarmam": ["16_PatchiVarmam"],
  "naemavarmam": ["17_NaemaVarmam"],
  "kannadikaalam": ["18_KannadiKaalam"],
  "paalavarmam": ["19_PaalaVarmam"],
  "chundigaivarmam": ["20_ChundigaiVarmam"],
  "minvettivarmam": ["21_Minvetti_L", "21_Minvetti_R"],
  "manthirakaalam": ["22_ManthiraKaalam_L", "22_ManthiraKaalam_R"],
  "puruvavarmam": ["23_Puruva_L", "23_Puruva_R"],
  "natchathirapvarmam": ["24_Natchathira_L", "24_Natchathira_R"],
  "kaamboodharikaalam": ["25_Kaamboodhari_L", "25_Kaamboodhari_R"],
  "valamoorthivarmam": ["26_ValamoorthiVarmam"],
  "konasannivarmam": ["27_Konasanni_L1", "27_Konasanni_R1"],
  "urakkakaalam": ["28_UrakkaKaalam_L", "28_UrakkaKaalam_R"],
  "udhirakaalam": ["29_UdhiraKaalam_L", "29_UdhiraKaalam_R"],
  "ottuvarmam": ["30_OttuVarmam"],
  "sanguthirivarmam": ["31_SanguthiriVarmam"],
  "sumaivarmam": ["32_SumaiVarmam"],
  "thummikalam": ["33_ThummiKaalam"],
  "kathirvarmam": ["34_KathirVarmam"],
  "kathirkaamavarmam": ["35_KathirKaamaVarmam"],
  "buththivarmam": ["36_BuththiVarmam"],
  "sakthivarmam": ["37_SakthiVarmam"],
  "koombuvarmam": ["38_KoombuVarmam"],
  "nervarmam": ["39_NerVarmam"],
  "aananthavayukalam": ["40_AananthaVayuKaalam"],
  "panrivarmam": ["41_PanriVarmam"],
  "utharakalam": ["42_UtharaVarmam"],
  "annakaalam": ["43_AnnaKaalam"],
  "thivalaivarmam": ["44_ThivalaiVarmam"],
  "thoosigavarmam": ["45_Thoosiga_L", "45_Thoosiga_R"],
  "anumarvarmam": ["46_Anumar_L", "46_Anumar_R"],
  "mundelluvarmam": ["47_Mundellu_L", "47_Mundellu_R"],
  "valiyaaththisurukkivarmam": ["48_ValiyaAththiSurukki_L", "48_ValiyaAththiSurukki_R"],
  "siriyaaththisurukkivarmam": ["49_SiriyaAththiSurukki_L", "49_SiriyaAththiSurukki_R"],
  "munsaruthivarmam": ["50_MunSaruthi_L", "50_MunSaruthi_R"],
  "pullaivarmam": ["51_Pallai_L", "51_Pallai_R"], // Spelling fix: Pullai? Check backend. Backend says "Pallai_Varmam" -> "Pallai"
  "pallaivarmam": ["51_Pallai_L", "51_Pallai_R"],
  "adappakalam": ["52_AdappaKaalam_L", "52_AdappaKaalam_R"],
  "vilanguvarmam": ["53_Vilangu_L", "53_Vilangu_R"],
  "asthikantharivarmam": ["54_Asthikanthari_L", "54_Asthikanthari_R"],
  "pujavarmam": ["55_Puja_L", "55_Puja_R"],
  "pirathaaraivarmam": ["56_Pirathaarai_L", "56_Pirathaarai_R"],
  "aendhivarmam": ["57_AendhiVarmam_L", "57_AendhiVarmam_R"],
  "kutthuvarmam": ["58_KutthuVarmam_L", "58_KutthuVarmam_R"],
  "asavuvarmam": ["59_AsavuVarmam_L", "59_AsavuVarmam_R"],
  "koachuvarmam": ["60_KoachuVarmam"],
  "kaimootuvarmam": ["61_Kaimootu_L", "61_Kaimootu_R"],
  "mudakkuvarmam": ["62_MudakkuVarmam"],
  "vishamanibanthavarmam": ["63_VishaManibantha_L", "63_VishaManibantha_R"],
  "manibanthavarmam": ["64_Manibantha_L", "64_Manibantha_R"],
  "thuthikkaivarmam": ["65_Thuthikkai_L", "65_Thuthikkai_R"],
  "ullangaivellaivarmam": ["66_UllangaiVellaiVarmam_L", "66_UllangaiVellaiVarmam_R"],
  "aanthaivarmam": ["67_AanthaiVarmam_L", "67_AanthaiVarmam_R"],
  "thatchanaikaalam": ["68_ThatchanaiKaalam_L", "68_ThatchanaiKaalam_R"], // Check if 68 exists
};

export const mapBackendToUnityNames = (backendNames) => {
  const mappedNames = new Set();

  backendNames.forEach(rawName => {
    // Normalize: remove underscores, convert to lowercase, remove spaces
    let normalized = rawName.toLowerCase().replace(/_/g, '').replace(/\s+/g, '');
    
    // Attempt direct lookup
    if (varmaMap[normalized]) {
        varmaMap[normalized].forEach(n => mappedNames.add(n));
        return;
    }

    // Attempt partial matches or specific manual fixes if needed
    // For now, rely on the extensive map above.
    
    // Logging for debugging unmapped names
    console.warn("Unmapped Varma Point:", rawName, "->", normalized);
  });

  return Array.from(mappedNames);
};
