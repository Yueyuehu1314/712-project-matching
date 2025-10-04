"""
Quick test script to verify the embedding analysis setup

This script performs a quick validation without running the full analysis.
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("EMBEDDING ANALYSIS SETUP TEST")
print("=" * 60)
print()

# Test 1: Check Python imports
print("[Test 1/5] Checking Python dependencies...")
try:
    import requests
    import numpy as np
    print("  ✓ requests")
    print("  ✓ numpy")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    print("\nInstall with: pip install requests numpy")
    sys.exit(1)

# Test 2: Check if Ollama is running
print("\n[Test 2/5] Checking Ollama service...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("  ✓ Ollama is running")
    else:
        print(f"  ✗ Ollama returned status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Cannot connect to Ollama: {e}")
    print("\nPlease start Ollama with: ollama serve")
    sys.exit(1)

# Test 3: Check if bge-m3 model is available
print("\n[Test 3/5] Checking bge-m3 model...")
try:
    models = response.json().get('models', [])
    model_names = [m['name'] for m in models]
    if any('bge-m3' in name for name in model_names):
        print("  ✓ bge-m3 model is available")
    else:
        print("  ✗ bge-m3 model not found")
        print(f"  Available models: {', '.join(model_names)}")
        print("\nPull the model with: ollama pull bge-m3")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Error checking models: {e}")
    sys.exit(1)

# Test 4: Check data directories
print("\n[Test 4/5] Checking data directories...")
projects_dir = Path("data/processed/projects_md")
profiles_dir = Path("data/processed/profiles_md")

if not projects_dir.exists():
    print(f"  ✗ Projects directory not found: {projects_dir}")
    sys.exit(1)
else:
    project_files = list(projects_dir.glob("**/*.md"))
    print(f"  ✓ Found {len(project_files)} project files")

if not profiles_dir.exists():
    print(f"  ✗ Profiles directory not found: {profiles_dir}")
    sys.exit(1)
else:
    profile_folders = [d for d in profiles_dir.iterdir() if d.is_dir()]
    total_profiles = sum(len(list(folder.glob("*.md"))) for folder in profile_folders)
    print(f"  ✓ Found {total_profiles} profile files across {len(profile_folders)} projects")

# Test 5: Test embedding generation (quick test)
print("\n[Test 5/5] Testing embedding generation...")
try:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "bge-m3", "prompt": "This is a test"},
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        embedding = result.get("embedding", [])
        if embedding:
            print(f"  ✓ Successfully generated test embedding (dimension: {len(embedding)})")
        else:
            print("  ✗ Embedding generation returned empty result")
            sys.exit(1)
    else:
        print(f"  ✗ Embedding API returned status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Error testing embedding generation: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED")
print("=" * 60)
print("\nYou can now run the full analysis:")
print("  ./run_full_embedding_analysis.sh")
print("\nOr run individual steps:")
print("  python src/experiments/embedding_similarity_comparison.py")
print("  python src/experiments/visualize_similarity_results.py")


