"""
Demonstration script showing custom evaluators working with actual results.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Import our custom evaluators
from exp_platform_cli import load_evaluators
from exp_platform_cli.models import DataModelRow, EvaluatorConfig

# Create some sample data like what the platform generates
sample_rows = [
    DataModelRow(
        id="row_0",
        data_input={"input": "Hello", "expected_output": "Hello! How can I help you today?"},
        data_output="Echo: Hello",
        expected_output="Hello! How can I help you today?",
    ),
    DataModelRow(
        id="row_1",
        data_input={"input": "What is 2+2?", "expected_output": "4"},
        data_output="Echo: What is 2+2?",
        expected_output="4",
    ),
    DataModelRow(
        id="row_2",
        data_input={"input": "Calculate 10*5", "expected_output": "50"},
        data_output="Echo: Calculate 10*5",
        expected_output="50",
    ),
]


def demo_custom_evaluators():
    """Demonstrate custom evaluators in action."""

    print("🧪 Custom Evaluators Demonstration")
    print("=" * 50)

    # Create evaluator configurations
    evaluator_configs = [
        EvaluatorConfig(id="length_eval", name="response_length", data_mapping={}),
        EvaluatorConfig(id="accuracy_eval", name="accuracy_checker", data_mapping={}),
        EvaluatorConfig(id="sentiment_eval", name="sentiment_evaluator", data_mapping={}),
    ]

    # Load the evaluators (this uses our registered custom evaluators)
    evaluators = load_evaluators(evaluator_configs)

    print(f"📊 Loaded {len(evaluators)} custom evaluators:")
    for evaluator in evaluators:
        print(f"   • {evaluator.__class__.__name__}")

    print("\n📋 Sample Data:")
    for i, row in enumerate(sample_rows, 1):
        print(f"   {i}. Input: '{row.data_input['input']}'")
        print(f"      Output: '{row.data_output}'")
        print(f"      Expected: '{row.expected_output}'")

    print("\n🔍 Evaluation Results:")
    print("-" * 50)

    # Run each evaluator
    for evaluator in evaluators:
        result = evaluator.evaluate(sample_rows)
        print(f"\n📈 {result.name.upper()} EVALUATOR:")
        print(f"   Summary: {result.summary}")
        print("   Per-row details:")
        for row_id, scores in result.per_row.items():
            print(f"      {row_id}: {scores}")


if __name__ == "__main__":
    demo_custom_evaluators()
