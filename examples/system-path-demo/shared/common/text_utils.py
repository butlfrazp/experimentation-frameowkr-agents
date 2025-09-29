"""
Shared utility functions that can be imported by evaluators.
"""

def calculate_readability_score(text: str) -> float:
    """Calculate a simple readability score."""
    if not text:
        return 0.0
    
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?') + 1
    
    if sentences == 0:
        return 0.0
    
    avg_words_per_sentence = len(words) / sentences
    
    # Simple readability metric (inverse of complexity)
    # Shorter sentences = higher readability
    if avg_words_per_sentence <= 10:
        return 1.0
    elif avg_words_per_sentence <= 20:
        return 0.7
    else:
        return 0.4


def extract_keywords(text: str) -> list[str]:
    """Extract important keywords from text."""
    if not text:
        return []
    
    # Simple keyword extraction
    words = text.lower().split()
    
    # Filter out common words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    
    return list(set(keywords))  # Remove duplicates