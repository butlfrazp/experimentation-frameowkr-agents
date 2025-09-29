#!/usr/bin/env python3
"""
Simple Examples Runner

Run all the simple Semantic Kernel examples in sequence.
"""

import asyncio
import sys
from pathlib import Path


async def run_example(example_file: str, example_name: str):
    """Run a single example."""
    print(f"\n{'='*60}")
    print(f"🚀 Running: {example_name}")
    print(f"📁 File: {example_file}")
    print("=" * 60)

    try:
        # Import and run the example
        example_path = Path(__file__).parent / example_file

        if not example_path.exists():
            print(f"❌ Example file not found: {example_file}")
            return False

        # Execute the example
        import subprocess

        result = subprocess.run(
            [sys.executable, str(example_path)], capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            print("✅ Example completed successfully!")
            print("\n📄 Output:")
            print("-" * 40)
            # Show last 15 lines of output to keep it manageable
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines[-15:]:
                print(line)
            print("-" * 40)
            return True
        else:
            print("❌ Example failed!")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Example timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running example: {e}")
        return False


async def main():
    """Run all simple examples."""
    print("🎯 Semantic Kernel Simple Examples Runner")
    print("=" * 50)

    # List of examples to run
    examples = [
        ("01_basic_math.py", "Basic Math Plugin"),
        ("02_basic_chat.py", "Basic Chat Functionality"),
        ("03_function_calling.py", "Function Calling"),
        ("04_conversation_flow.py", "Conversation Flow"),
    ]

    print(f"📋 Found {len(examples)} examples to run")

    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "01_basic_math.py").exists():
        print("❌ Not in the simple_examples directory!")
        print("Please run this script from: examples/semantic_kernel/simple_examples/")
        return

    # Run examples
    successful = 0
    failed = 0

    for example_file, example_name in examples:
        success = await run_example(example_file, example_name)
        if success:
            successful += 1
        else:
            failed += 1

        # Short pause between examples
        await asyncio.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("📊 Examples Summary")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(
        f"📈 Success Rate: {(successful/(successful+failed)*100):.1f}%"
        if (successful + failed) > 0
        else "N/A"
    )

    if failed == 0:
        print("\n🎉 All examples completed successfully!")
    else:
        print(f"\n⚠️  {failed} example(s) had issues. Check output above for details.")

    print("\n💡 Tip: Run individual examples with:")
    print("   python 01_basic_math.py")
    print("   python 02_basic_chat.py")
    print("   etc.")


if __name__ == "__main__":
    asyncio.run(main())
