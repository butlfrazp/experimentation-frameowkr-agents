"""
Simple test script to verify that python_path functionality works.
"""

import sys
from pathlib import Path

# Add the nested directories to Python path (simulating what the platform should do)
current_dir = Path(__file__).parent
nested_paths = ["nested/deep/evaluators", "utils/helpers", "shared/common"]

print("🔧 Testing Python Path Setup")
print("=" * 40)

# Add paths to sys.path
original_paths = sys.path.copy()
for path_str in nested_paths:
    full_path = str(current_dir / path_str)
    if full_path not in sys.path:
        sys.path.insert(0, full_path)
        print(f"✅ Added: {full_path}")

print("\n📦 Testing imports:")

try:
    import complex_evaluator

    print("✅ Successfully imported complex_evaluator")
except ImportError as e:
    print(f"❌ Failed to import complex_evaluator: {e}")

try:
    import utility_eval

    print("✅ Successfully imported utility_eval")
except ImportError as e:
    print(f"❌ Failed to import utility_eval: {e}")

try:
    from text_utils import calculate_readability_score

    print("✅ Successfully imported text_utils functions")
except ImportError as e:
    print(f"❌ Failed to import text_utils: {e}")

# Test the evaluator registration
print("\n🧪 Testing evaluator registration:")
from exp_platform_cli.evaluators.registry import registry

print(f"📊 Registered evaluators: {list(registry._evaluators.keys())}")

# Restore original sys.path
sys.path[:] = original_paths
print("\n🔄 Restored original sys.path")
