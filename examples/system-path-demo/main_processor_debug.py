"""
Enhanced processor that shows exactly where python_path directories are resolved from.
"""

import sys
from pathlib import Path

# Import evaluators from nested paths (made possible by python_path config)
try:
    # These imports work because the directories are added to sys.path
    import complex_evaluator  # from nested/deep/evaluators/
    import utility_eval  # from utils/helpers/
    from text_utils import calculate_readability_score, extract_keywords  # from shared/common/

    print("✅ Successfully imported from all nested directories via python_path!")

    # Show exactly where paths were resolved from
    current_cwd = Path.cwd()
    added_paths = [p for p in sys.path if "system-path-demo" in p]

    print(f"📍 Current working directory: {current_cwd}")
    print(f"📍 Added Python paths ({len(added_paths)}):")
    for path in added_paths:
        relative_to_cwd = (
            Path(path).relative_to(current_cwd)
            if current_cwd in Path(path).parents or current_cwd == Path(path)
            else "Not relative to CWD"
        )
        print(f"   • {path}")
        print(f"     → Relative to CWD: {relative_to_cwd}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print(f"📍 Current working directory: {Path.cwd()}")
    print("📍 Current sys.path entries containing 'system-path':")
    for path in sys.path:
        if "system-path" in path:
            print(f"   • {path}")


def run(**kwargs) -> str:
    """
    Process input using modules from custom python_path directories.
    Shows path resolution details.

    Args:
        **kwargs: All data fields from the dataset row

    Returns:
        The processed response with path info
    """
    input_text = kwargs.get("input", "No input provided")

    # Show path resolution details
    current_cwd = Path.cwd()
    added_paths = [p for p in sys.path if "system-path-demo" in p]

    # Use shared utilities (if available)
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

    # Add path resolution info
    response += f" | CWD: {current_cwd.name}"
    response += f" | Loaded from {len(added_paths)} custom paths"

    # Include path details in response for verification
    if added_paths:
        response += f" | First path: {Path(added_paths[0]).name}"

    return response


if __name__ == "__main__":
    # Test the system path functionality
    print("🧪 Testing System Path Demo - Path Resolution Details")
    print("=" * 60)

    # Show current Python path
    print(f"📁 Current Working Directory: {Path.cwd()}")
    print("📁 Added Python paths:")
    for path in sys.path:
        if "system-path-demo" in path:
            print(f"   • {path}")

    # Test the processing
    test_result = run(input="Hello world! How are you today?")
    print(f"\n📋 Test Result: {test_result}")
