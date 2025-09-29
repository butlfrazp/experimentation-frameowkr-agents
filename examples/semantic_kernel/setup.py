#!/usr/bin/env python3
"""
Setup script for Semantic Kernel Simple Examples

This script helps you get started with the simple examples.
"""

import os
import sys
from pathlib import Path


def check_requirements():
    """Check if required packages are installed."""
    print("🔍 Checking requirements...")
    
    try:
        import semantic_kernel
        print("✅ semantic-kernel is installed")
        sk_version = getattr(semantic_kernel, '__version__', 'unknown')
        print(f"   Version: {sk_version}")
    except ImportError:
        print("❌ semantic-kernel is not installed")
        print("   Install with: pip install 'semantic-kernel>=1.0.0'")
        return False
    
    try:
        import openai
        print("✅ openai is installed")
        openai_version = getattr(openai, '__version__', 'unknown')
        print(f"   Version: {openai_version}")
    except ImportError:
        print("❌ openai is not installed")
        print("   Install with: pip install 'openai>=1.0.0'")
        return False
    
    return True


def check_api_key():
    """Check if OpenAI API key is configured."""
    print("\n🔑 Checking API key configuration...")
    
    # Check environment variable
    env_key = os.getenv("OPENAI_API_KEY")
    
    # Check .env file
    env_file = Path(".env")
    env_file_key = None
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip().startswith("OPENAI_API_KEY="):
                        env_file_key = line.split("=", 1)[1].strip()
                        if env_file_key and not env_file_key.startswith("your-"):
                            print("✅ API key found in .env file")
                            return True
        except Exception as e:
            print(f"⚠️  Error reading .env file: {e}")
    
    if env_key:
        print("✅ API key found in environment variable")
        return True
    
    print("❌ OpenAI API key not found")
    print("   Set environment variable: export OPENAI_API_KEY='your-key-here'")
    print("   Or create .env file with: OPENAI_API_KEY=your-key-here")
    return False


def setup_env_file():
    """Create .env file from template."""
    print("\n📝 Setting up .env file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        response = input("📄 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing .env file")
            return True
    
    try:
        # Copy example file
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✅ .env file created from template")
        print("   Please edit .env and add your OpenAI API key")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False





def run_quick_test():
    """Run the simple examples."""
    print("\n🧪 Running simple examples (no API required)...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "run_all.py"], 
                              cwd="simple_examples",
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Simple examples completed successfully!")
            print("   Last few lines of output:")
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:
                print(f"   {line}")
            return True
        else:
            print("❌ Simple examples failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Simple examples timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Semantic Kernel Simple Examples Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return
    
    # Run all checks
    requirements_ok = check_requirements()
    
    if not requirements_ok:
        print("\n📦 To install requirements, run:")
        print("   pip install -r requirements.txt")
        print("\n🧪 You can still run the simple examples:")
        print("   cd simple_examples && python run_all.py")
        
        response = input("\n🤔 Run simple examples now? (Y/n): ")
        if response.lower() != 'n':
            run_quick_test()
        return
    
    api_key_ok = check_api_key()
    
    if not api_key_ok:
        response = input("\n🤔 Create .env file from template? (Y/n): ")
        if response.lower() != 'n':
            setup_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Summary")
    print("=" * 50)
    
    print(f"Requirements: {'✅' if requirements_ok else '❌'}")
    print(f"API Key: {'✅' if api_key_ok else '❌'}")
    
    if requirements_ok and api_key_ok:
        print("\n🚀 You're ready to go! Try these commands:")
        print("   cd simple_examples")
        print("   python run_all.py                # Run all examples")
        print("   python 01_basic_math.py          # Start with math basics")
    
    elif requirements_ok:
        print("\n⚠️  Set up your API key and you'll be ready!")
        print("   cd simple_examples && python run_all.py  # Mock test (no API)")
    
    else:
        print("\n📝 Next steps:")
        print("   1. pip install -r requirements.txt")
        print("   2. Set up your OpenAI API key")
        print("   3. Run python setup.py again")
    
    print("\n📚 For detailed instructions, see simple_examples/README.md")


if __name__ == "__main__":
    main()