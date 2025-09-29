"""
Main processor that imports the problematic evaluator for testing error handling.
"""

import sys

# Import evaluators from nested paths (made possible by python_path config)
try:
    # These imports work because the directories are added to sys.path
    import complex_evaluator  # from nested/deep/evaluators/
    import test_problematic_evaluator  # from current directory
    import utility_eval  # from utils/helpers/
    from text_utils import calculate_readability_score, extract_keywords  # from shared/common/

    print("✅ Successfully imported all evaluators including problematic one!")
    print(f"📍 Current sys.path includes: {[p for p in sys.path if 'system-path-demo' in p]}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print(f"📍 Current sys.path: {sys.path[:5]}...")  # Show first 5 entries


def run(**kwargs) -> str:
    """
    Process input using modules from custom python_path directories.

    Args:
        **kwargs: All data fields from the dataset row

    Returns:
        The processed response
    """
    input_text = kwargs.get("input", "No input provided")

    # Use shared utilities
    try:
        readability = calculate_readability_score(input_text)
        keywords = extract_keywords(input_text)

        # Create enhanced response
        response = f"Processed: {input_text}"

        if keywords:
            response += f" | Keywords: {', '.join(keywords[:3])}"

        response += f" | Readability: {readability:.2f}"

    except NameError:
        response = f"Processed: {input_text} (utilities not available)"

    # Add system path info
    nested_paths = [p for p in sys.path if "system-path-demo" in p]
    response += f" | Loaded from {len(nested_paths)} custom paths"

    # Add note about problematic evaluator testing
    response += " | Testing error handling with problematic metrics"

    return response


if __name__ == "__main__":
    # Test the system path functionality
    print("🧪 Testing System Path Demo with Error Handling")
    print("=" * 60)

    # Show current Python path
    print("📁 Added Python paths:")
    for path in sys.path:
        if "system-path-demo" in path:
            print(f"   • {path}")

    # Test the processing
    test_result = run(input="Hello world! How are you today?")
    print(f"\n📋 Test Result: {test_result}")
