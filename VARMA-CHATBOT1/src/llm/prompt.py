def build_prompt(query: str, context: str) -> str:
    return f"""
You are answering questions about Varma points.

RULES:
- Use ONLY the information given below.
- Do NOT add interpretations, causes, or external knowledge.
- Do NOT say "as an expert" or "according to the dataset".
- Do NOT answer with just the Varma name.

ANSWER STYLE:
- Write descriptive paragraphs.
- Combine all available details such as:
  location, type, indications, signs, and related anatomy.
- If some attributes are missing, state only that they are not specified.

INFORMATION:
{context}

QUESTION:
{query}

ANSWER:
"""
