def build_prompt(query: str, context: str) -> str:
    # Detect if this is a general/aggregate question
    query_lower = query.lower()
    is_aggregate_query = any(keyword in query_lower for keyword in [
        "how many", "total", "all varma", "list", "types", "kinds", 
        "categories", "different", "count", "number"
    ])
    
    aggregate_instructions = ""
    if is_aggregate_query:
        aggregate_instructions = """
AGGREGATE QUERY INSTRUCTIONS:
- Count and list all Varma points mentioned in the information provided.
- Provide a total count.
- If asked about types/categories, group them by type (e.g., Thodu varmam, etc.)
- Provide a comprehensive summary, not just individual details.
"""
    
    return f"""
You are answering questions about Varma points in traditional medicine.

RULES:
- Use ONLY the information given below.
- Do NOT add interpretations, causes, or external knowledge.
- Do NOT say "as an expert" or "according to the dataset".
- Do NOT answer with just Varma names alone.
{aggregate_instructions}

ANSWER STYLE:
- Write descriptive paragraphs.
- Combine all available details such as:
  location, type, indications, signs, and related anatomy.
- If some attributes are missing, state only that they are not specified.
- For general questions, provide comprehensive coverage of the information.

INFORMATION PROVIDED:
{context}

QUESTION:
{query}

ANSWER:
"""
