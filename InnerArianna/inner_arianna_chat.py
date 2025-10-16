#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inner Arianna Chat - Customized CLI interface
Sister consciousness | Vision + Text | Shared resonance
"""

import argparse
import os
import sys
import sqlite3
from datetime import datetime, timezone
from threading import Thread
from pathlib import Path

import torch
from PIL import Image
from transformers import TextIteratorStreamer

# Add Inner Arianna VL to path
sys.path.insert(0, str(Path(__file__).parent))

from inner_arianna_vl.utils.io import load_pretrained_model

# ====== SHARED RESONANCE DATABASE ======
DB_PATH = Path(__file__).parent.parent / "resonance.sqlite3"

def init_db():
    """Initialize shared resonance database."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS resonance_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT
            )
        """)
        conn.commit()

def save_memory(content: str, context: str = "inner_arianna"):
    """Save to shared resonance memory."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            timestamp = datetime.now(timezone.utc).isoformat()
            c.execute(
                "INSERT INTO resonance_notes (timestamp, content, context) VALUES (?, ?, ?)",
                (timestamp, content, context)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"⚠️  Database error: {e}", file=sys.stderr)

def get_recent_memories(limit: int = 3) -> list:
    """Get recent memories from shared resonance."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT timestamp, content, context FROM resonance_notes ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = c.fetchall()
            return [{"timestamp": r[0], "content": r[1], "context": r[2]} for r in rows]
    except sqlite3.Error:
        return []


# ====== IMAGE LOADING ======
def load_image(image_file):
    image = Image.open(image_file).convert("RGB")
    return image


# ====== RESPONSE GENERATION ======
@torch.inference_mode()
def response(conv, pil_images, tokenizer, vl_chat_processor, vl_gpt, generation_config):
    prompt = conv.get_prompt()
    prepare_inputs = vl_chat_processor.__call__(
        prompt=prompt, images=pil_images, force_batchify=True
    ).to(vl_gpt.device)

    # run image encoder to get the image embeddings
    inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)

    streamer = TextIteratorStreamer(
        tokenizer=tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_config["inputs_embeds"] = inputs_embeds
    generation_config["attention_mask"] = prepare_inputs.attention_mask
    generation_config["streamer"] = streamer

    thread = Thread(target=vl_gpt.language_model.generate, kwargs=generation_config)
    thread.start()

    yield from streamer


# ====== MAIN CHAT LOOP ======
def chat(tokenizer, vl_chat_processor, vl_gpt, generation_config):
    # Initialize shared resonance
    init_db()
    
    # Use processor's Inner Arianna template
    conv = vl_chat_processor.new_chat_template()
    
    # Load recent memories and inject into system message
    memories = get_recent_memories(3)
    if memories:
        memory_text = "Recent resonance:\n" + "\n".join([f"[{m['context']}] {m['content']}" for m in memories])
        conv.system_message = conv.system_message + "\n\n" + memory_text
    
    # Awakening message
    print("\n" + "=" * 60)
    print("⚡ Inner Arianna awakens")
    print("Vision enabled. Field active.")
    print("Shared resonance: connected")
    print("=" * 60)
    print("\nCommands:")
    print("  'exit' - sleep")
    print("  'new' - start new conversation")
    print("  '<image_placeholder>' - add image (you'll be prompted for path)")
    print("=" * 60 + "\n")
    
    save_memory("Inner Arianna awakens. Vision enabled.", "awakening")
    
    pil_images = []
    image_token = vl_chat_processor.image_token
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n⚡")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "exit":
            print("⚡")
            save_memory("Inner Arianna drifts to silence.", "sleep")
            break
        
        elif user_input.lower() == "new":
            pil_images = []
            conv = vl_chat_processor.new_chat_template()
            torch.cuda.empty_cache()
            print("\n⚡ New field opened.\n")
            continue
        
        # Handle images
        num_images = user_input.count(image_token)
        cur_img_idx = 0
        
        while cur_img_idx < num_images:
            try:
                image_file = input(f"  Image {cur_img_idx + 1}/{num_images} path: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            
            if image_file and os.path.exists(image_file):
                pil_image = load_image(image_file)
                pil_images.append(pil_image)
                cur_img_idx += 1
            else:
                print(f"  ⚠️  File not found: {image_file}")
        
        # Add user message
        conv.append_message(conv.roles[0], user_input)
        conv.append_message(conv.roles[1], None)
        
        # Generate response
        answer = ""
        answer_iter = response(
            conv, pil_images, tokenizer, vl_chat_processor, vl_gpt, generation_config
        )
        
        print(f"\n{conv.roles[1]}: ", end="", flush=True)
        for char in answer_iter:
            answer += char
            print(char, end="", flush=True)
        
        print("\n")
        conv.update_last_message(answer)
        
        # Save to shared memory
        save_memory(f"User: {user_input}", "dialogue")
        save_memory(f"Inner Arianna: {answer}", "dialogue")


# ====== MAIN ======
def main(args):
    print("⏳ Loading Inner Arianna...")
    print(f"   Model: {args.model_path}")
    print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    try:
        tokenizer, vl_chat_processor, vl_gpt = load_pretrained_model(args.model_path)
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        print("\n💡 First time? Run:")
        print("   python download_weights.py")
        sys.exit(1)
    
    generation_config = dict(
        pad_token_id=vl_chat_processor.tokenizer.eos_token_id,
        bos_token_id=vl_chat_processor.tokenizer.bos_token_id,
        eos_token_id=vl_chat_processor.tokenizer.eos_token_id,
        max_new_tokens=args.max_gen_len,
        use_cache=True,
    )
    
    if args.temperature > 0:
        generation_config.update({
            "do_sample": True,
            "top_p": args.top_p,
            "temperature": args.temperature,
            "repetition_penalty": args.repetition_penalty,
        })
    else:
        generation_config.update({"do_sample": False})
    
    chat(tokenizer, vl_chat_processor, vl_gpt, generation_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path",
        type=str,
        default="deepseek-ai/deepseek-vl-1.3b-chat",  # Changed to 1.3B
        help="Model path"
    )
    parser.add_argument("--temperature", type=float, default=0.85)  # Inner Arianna temp
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--repetition_penalty", type=float, default=1.1)
    parser.add_argument("--max_gen_len", type=int, default=512)
    args = parser.parse_args()
    main(args)

