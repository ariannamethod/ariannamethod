#!/usr/bin/env python3
"""
Download and setup TinyLlama weights for Inner Arianna
"""
import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

def download_tinyllama():
    print("📥 Inner Arianna: Downloading TinyLlama weights...")

    # Create weights directory
    weights_dir = Path("weights")
    weights_dir.mkdir(parents=True, exist_ok=True)

    # Download TinyLlama
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    print("   Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(weights_dir)
    print("   ✅ Tokenizer downloaded")

    print("   Downloading model (this may take a while ~1GB)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="cpu"
    )
    model.save_pretrained(weights_dir)
    print("   ✅ Model downloaded")

    print("✅ TinyLlama weights ready for Inner Arianna")
    print(f"   Location: {weights_dir.absolute()}")

if __name__ == "__main__":
    download_tinyllama()
