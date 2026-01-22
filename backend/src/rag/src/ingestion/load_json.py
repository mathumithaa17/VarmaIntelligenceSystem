import json


def load_varma_json(path: str):
    """
    Loads Varma data from the given JSON file and converts
    each Varma point into a text document suitable for RAG.
    """

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    # Your JSON root key is "varmas"
    for item in data["varmas"]:
        anatomy = item.get("anatomicalRelations", {})

        text = (
            f"Varma Name: {item.get('varmaName', '')}\n\n"
            f"Signs:\n{item.get('signs', '')}\n\n"
            f"Pathognomic Sign:\n{item.get('pathognomicSign', '')}\n\n"
            f"Indications:\n{item.get('indications', '')}\n\n"
            f"Surface Anatomy:\n{item.get('surfaceAnatomy', '')}\n\n"
            f"Varmam Type:\n{item.get('varmamType', '')}\n\n"
            f"Laterality:\n{item.get('laterality', '')}\n\n"
            f"Synonyms:\n{item.get('synonyms', '')}\n\n"
            f"Tamil Literature:\n{item.get('tamilLiterature', '')}\n\n"
            f"Anatomical Relations:\n"
            f"Muscles: {anatomy.get('muscles', '')}\n"
            f"Arteries: {anatomy.get('arteries', '')}\n"
            f"Veins: {anatomy.get('veins', '')}\n"
            f"Nerves: {anatomy.get('nerves', '')}"
        )

        documents.append({
            "id": item.get("varmaName", ""),
            "text": text
        })

    return documents
