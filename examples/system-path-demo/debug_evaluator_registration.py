"""
Debug script to check what evaluators are registered when python_path is used.
"""

import sys
from pathlib import Path

# First, add the paths manually (simulating python_path)
current_dir = Path(__file__).parent
nested_paths = ["nested/deep/evaluators", "utils/helpers", "shared/common"]

print("🔧 Adding custom paths to sys.path:")
for path_str in nested_paths:
    full_path = str(current_dir / path_str)
    if full_path not in sys.path:
        sys.path.insert(0, full_path)
        print(f"✅ Added: {full_path}")

# Now import the evaluator modules to register them
print("\n📦 Importing evaluator modules:")
try:
    import complex_evaluator

    print("✅ Imported complex_evaluator")
except ImportError as e:
    print(f"❌ Failed to import complex_evaluator: {e}")

try:
    import utility_eval

    print("✅ Imported utility_eval")
except ImportError as e:
    print(f"❌ Failed to import utility_eval: {e}")

# Check what evaluators are registered
print("\n🧪 Checking registered evaluators:")
from exp_platform_cli.evaluators.registry import registry

print(f"📊 Registry type: {type(registry)}")
print(f"📊 Available evaluators: {list(registry.available())}")

# Try to create the evaluators we expect
from exp_platform_cli.models import EvaluatorConfig

test_configs = [
    EvaluatorConfig(id="deep_nested_eval", name="deep_nested_evaluator", data_mapping={}),
    EvaluatorConfig(id="utils_eval", name="utility_evaluator", data_mapping={}),
]

print("\n🎯 Testing evaluator creation:")
for config in test_configs:
    evaluator = registry.create(config)
    if evaluator:
        print(f"✅ Created evaluator: {config.name} -> {evaluator.__class__.__name__}")
    else:
        print(f"❌ Failed to create evaluator: {config.name}")

print(f"\n📍 Total registered evaluators: {len(list(registry.available()))}")
print(f"📍 Evaluator names: {', '.join(registry.available())}")
