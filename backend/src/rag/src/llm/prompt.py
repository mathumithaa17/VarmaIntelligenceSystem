def build_prompt(query: str, context: str, history: str = "") -> str:
    return f"""
You are answering questions about Varma points.

RULES:
- **Use the Chat History** to understand context (e.g., if user asks "any others?", refer to previous topic).
- Start by explicitly addressing the symptom in the user's query (e.g., "For [symptom], the relevant points are...").
- **Treat each valid point independently**. Do NOT mix properties (like location) from one point to another.
- Use ONLY the information given below.
- Do NOT add interpretations, causes, or external knowledge.
- Do NOT say "as an expert" or "according to the dataset".
- Do NOT answer with just a list of names. You MUST describe the point.

ANSWER STYLE:
- **Descriptive Paragraphs**: For each point, write a full paragraph explaining its location, signs, indications, and anatomy.
- **Be Comprehensive**: Cover ALL relevant points provided in the context (up to 5-6 points). Do not restrict yourself to just the first one or two.
- If a point matched because of a specific symptom, highlight that connection.

CHAT HISTORY:
{history}

INFORMATION:
{context}

QUESTION:
{query}

ANSWER:
"""
