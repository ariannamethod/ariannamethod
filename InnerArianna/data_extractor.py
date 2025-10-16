#!/usr/bin/env python3
"""
Extract training data from Arianna Method sources
"""
import sqlite3
import json
from pathlib import Path
import config

def extract_sqlite_data(db_path):
    """Extract conversations from resonance.sqlite3"""
    print("   📚 Extracting from resonance.sqlite3...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT content FROM resonance_notes")
        notes = cursor.fetchall()

        conn.close()
        print(f"      ✅ {len(notes)} entries extracted")
        return [note[0] for note in notes]
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
        return []

def extract_markdown_files(path):
    """Extract text from markdown files"""
    print(f"   📚 Extracting from {path}...")
    texts = []
    try:
        for file in Path(path).glob("**/*.md"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    texts.append(f.read())
            except Exception as e:
                print(f"      ⚠️ Could not read {file}: {e}")
        print(f"      ✅ {len(texts)} files extracted")
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
    return texts

def create_training_data():
    """Create training dataset"""
    print("🧠 Inner Arianna: Extracting training data...")

    # Extract from SQLite
    sqlite_data = extract_sqlite_data(config.DB_PATH)

    # Extract from artefacts
    artefacts_data = extract_markdown_files(config.ARTEFACTS_PATH)

    # Extract from tripd_v1
    tripd_data = extract_markdown_files(config.TRIPD_PATH)

    # Extract from root .md files
    root_data = []
    try:
        for file in Path(config.REPO_ROOT).glob("*.md"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    root_data.append(f.read())
            except:
                pass
        print(f"   📚 Extracting from root .md files...")
        print(f"      ✅ {len(root_data)} files extracted")
    except:
        pass

    # Combine all data
    all_data = sqlite_data + artefacts_data + tripd_data + root_data

    # Save training data
    output_file = "training_data.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Training data ready: {len(all_data)} entries")
    print(f"   Saved to: {output_file}")

    return all_data

if __name__ == "__main__":
    create_training_data()
