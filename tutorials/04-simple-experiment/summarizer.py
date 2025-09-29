"""
Simple text summarization module for learning experiment construction.
"""

def run(input: str, max_length: int = 100, **kwargs) -> str:
    """
    Simple text summarization using sentence extraction.
    
    Args:
        input: The article text to summarize
        max_length: Maximum length for the summary (not used in this simple version)
        **kwargs: Additional arguments (e.g., expected_output, context)
        
    Returns:
        A summary of the input text
    """
    # Split into sentences
    sentences = input.split('.')
    
    # Clean up sentences and remove empty ones
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    
    if not clean_sentences:
        return "Unable to generate summary."
    
    # Simple heuristic: take first two sentences
    # In a real application, you might use more sophisticated methods
    summary_sentences = clean_sentences[:2]
    
    # Join the sentences back together
    summary = '. '.join(summary_sentences)
    
    # Ensure proper ending
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary


def advanced_run(input_data: str, max_length: int = 100) -> str:
    """
    More sophisticated summarization with sentence scoring.
    
    This is an example of how you might improve the summarizer.
    """
    sentences = input_data.split('.')
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    
    if not clean_sentences:
        return "Unable to generate summary."
    
    # Score sentences by position and length
    scored_sentences = []
    for i, sentence in enumerate(clean_sentences):
        # Earlier sentences get higher position scores
        position_score = len(clean_sentences) - i
        
        # Longer sentences (within reason) get higher content scores
        length_score = min(len(sentence.strip()), 200) / 200
        
        # Combined score
        total_score = position_score * 0.7 + length_score * 0.3
        scored_sentences.append((total_score, sentence))
    
    # Sort by score and take top 2
    scored_sentences.sort(reverse=True)
    summary_sentences = [s[1] for s in scored_sentences[:2]]
    
    # Maintain original order in the summary
    summary_sentences.sort(key=lambda x: clean_sentences.index(x))
    
    return '. '.join(summary_sentences) + '.'


# Example usage and testing
if __name__ == "__main__":
    test_article = """
    Artificial intelligence is transforming industries worldwide. 
    Companies are investing billions in AI research and development. 
    Machine learning algorithms are becoming more sophisticated every year. 
    The future of AI looks incredibly promising with new breakthroughs happening regularly.
    """
    
    print("Simple Summarization:")
    print(run(test_article))
    print("\nAdvanced Summarization:")
    print(advanced_run(test_article))