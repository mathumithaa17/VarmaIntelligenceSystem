def grounded(response: str, context: str, threshold: float = 0.3) -> bool:
    context_words = set(context.lower().split())
    response_words = set(response.lower().split())

    overlap = context_words & response_words
    return len(overlap) / max(len(response_words), 1) >= threshold
