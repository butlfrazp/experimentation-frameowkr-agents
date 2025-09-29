"""
Diagnostic script to check evaluator output types and catch float conversion errors.
Use this to debug your evaluators before running experiments.
"""


def diagnose_evaluator_outputs():
    """Test evaluator outputs for type compatibility."""

    print("🔍 Evaluator Output Diagnostics")
    print("=" * 50)

    # Import the platform
    try:
        from exp_platform_cli import BaseEvaluator, EvaluatorOutput
        from exp_platform_cli.evaluators.registry import registry
        from exp_platform_cli.models import DataModelRow, EvaluatorConfig

        print("✅ Platform imports successful")
    except ImportError as e:
        print(f"❌ Platform import failed: {e}")
        return

    # Check available evaluators
    available_evaluators = list(registry.available())
    print(f"📊 Available evaluators: {available_evaluators}")

    if not available_evaluators:
        print("⚠️  No evaluators found! Make sure to import your evaluator modules first.")
        return

    # Create test data
    test_rows = [
        DataModelRow(
            id="test_0",
            data_input={"input": "Hello world!"},
            data_output="Test response 1",
            expected_output="Expected response",
        ),
        DataModelRow(
            id="test_1",
            data_input={"input": "What is 2+2?"},
            data_output="Test response 2",
            expected_output="4",
        ),
    ]

    print(f"\n🧪 Testing {len(test_rows)} sample rows")

    # Test each evaluator
    for evaluator_name in available_evaluators:
        print(f"\n📋 Testing evaluator: {evaluator_name}")

        try:
            # Create evaluator config
            config = EvaluatorConfig(
                id=f"test_{evaluator_name}", name=evaluator_name, data_mapping={}
            )

            # Create evaluator instance
            evaluator = registry.create(config)
            if not evaluator:
                print(f"❌ Failed to create evaluator: {evaluator_name}")
                continue

            # Run evaluation
            result = evaluator.evaluate(test_rows)

            # Check result type
            if not isinstance(result, EvaluatorOutput):
                print(f"❌ Wrong return type: {type(result)} (expected EvaluatorOutput)")
                continue

            print("✅ Evaluator executed successfully")

            # Check summary metrics
            print("📊 Summary metrics:")
            for key, value in result.summary.items():
                value_type = type(value).__name__
                is_numeric = isinstance(value, (int, float))
                print(
                    f"   • {key}: {value} ({value_type}) {'✅' if is_numeric else '❌ NOT NUMERIC'}"
                )

                if not is_numeric:
                    print(
                        f"     ⚠️  WARNING: '{key}' is not numeric - this may cause float conversion errors!"
                    )

            # Check per-row metrics
            if result.per_row:
                print("📋 Per-row metrics (sample from first row):")
                first_row_id = next(iter(result.per_row.keys()))
                first_row_metrics = result.per_row[first_row_id]

                for key, value in first_row_metrics.items():
                    value_type = type(value).__name__
                    is_numeric = isinstance(value, (int, float))
                    print(
                        f"   • {key}: {value} ({value_type}) {'✅' if is_numeric else '❌ NOT NUMERIC'}"
                    )

                    if not is_numeric:
                        print(
                            f"     ⚠️  WARNING: '{key}' is not numeric - this may cause float conversion errors!"
                        )

        except Exception as e:
            print(f"❌ Evaluator failed: {e}")
            import traceback

            traceback.print_exc()

    print("\n🎯 Diagnostic Complete!")
    print("📝 To fix float conversion errors:")
    print("   1. Ensure all metric values are int or float")
    print("   2. Convert booleans: True -> 1.0, False -> 0.0")
    print("   3. Handle None values: None -> 0.0")
    print("   4. Convert strings: '0.5' -> 0.5")


if __name__ == "__main__":
    diagnose_evaluator_outputs()
