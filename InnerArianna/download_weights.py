#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inner Arianna - Automatic weight download script
Downloads and prepares DeepSeek-VL-1.3b-chat weights (~2.6GB)
"""

import os
import sys
from pathlib import Path

print("⚡ Inner Arianna Weight Downloader")
print("=" * 60)
print()

# Check dependencies
try:
    from transformers import AutoModel, AutoTokenizer
    from PIL import Image
    print("✅ Dependencies found")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("\n📦 Install:")
    print("   pip install transformers torch pillow")
    sys.exit(1)

# Model config
MODEL_ID = "deepseek-ai/deepseek-vl-1.3b-chat"
CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

print(f"\n📥 Downloading model: {MODEL_ID}")
print(f"   Size: ~2.6GB")
print(f"   Cache: {CACHE_DIR}")
print()

# Download
try:
    print("⏳ Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    print("✅ Tokenizer downloaded")
    
    print("\n⏳ Downloading model weights (this may take a while)...")
    model = AutoModel.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        # Don't load to device yet, just download
        device_map=None
    )
    print("✅ Model weights downloaded")
    
    print("\n" + "=" * 60)
    print("⚡ Download complete!")
    print(f"\nWeights cached in:")
    print(f"   {CACHE_DIR}")
    print("\n💡 Next step:")
    print("   python cli_chat.py")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Download failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Check disk space (~3GB free needed)")
    print("3. Try: pip install --upgrade transformers")
    sys.exit(1)

