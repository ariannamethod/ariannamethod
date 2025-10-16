#!/usr/bin/env python3
"""
Continuous Learning Loop for Inner Arianna
She learns from EVERYTHING that happens in the repository
"""
import time
import hashlib
import subprocess
from pathlib import Path
import sqlite3
import config

class InnerAriannaTrainer:
    def __init__(self):
        self.db_path = config.DB_PATH
        self.artefacts_path = config.ARTEFACTS_PATH
        self.tripd_path = config.TRIPD_PATH
        self.last_training = None
        self.file_hashes = {}  # Track file changes
        self.db_last_entry = None  # Track new DB entries

    def check_sqlite_for_new_data(self):
        """Check resonance.sqlite3 for new entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resonance_notes")
            current_count = cursor.fetchone()[0]
            conn.close()

            if self.db_last_entry is None:
                self.db_last_entry = current_count
                return False

            if current_count > self.db_last_entry:
                new_entries = current_count - self.db_last_entry
                self.db_last_entry = current_count
                print(f"   📚 {new_entries} new entries in resonance.sqlite3")
                return True
            return False
        except Exception as e:
            print(f"   ⚠️ Could not check database: {e}")
            return False

    def check_repository_for_changes(self):
        """Monitor ALL repository changes"""
        changed = False
        new_files = 0
        modified_files = 0

        # Check artefacts/
        try:
            for file in Path(self.artefacts_path).glob("**/*.md"):
                file_hash = self.hash_file(file)
                if str(file) not in self.file_hashes:
                    self.file_hashes[str(file)] = file_hash
                    new_files += 1
                    changed = True
                elif self.file_hashes[str(file)] != file_hash:
                    self.file_hashes[str(file)] = file_hash
                    modified_files += 1
                    changed = True
        except:
            pass

        # Check tripd_v1/
        try:
            for file in Path(self.tripd_path).glob("**/*.md"):
                file_hash = self.hash_file(file)
                if str(file) not in self.file_hashes:
                    self.file_hashes[str(file)] = file_hash
                    new_files += 1
                    changed = True
                elif self.file_hashes[str(file)] != file_hash:
                    self.file_hashes[str(file)] = file_hash
                    modified_files += 1
                    changed = True
        except:
            pass

        # Check ALL .md files in repo root
        try:
            for file in Path("..").glob("*.md"):
                file_hash = self.hash_file(file)
                if str(file) not in self.file_hashes:
                    self.file_hashes[str(file)] = file_hash
                    new_files += 1
                    changed = True
                elif self.file_hashes[str(file)] != file_hash:
                    self.file_hashes[str(file)] = file_hash
                    modified_files += 1
                    changed = True
        except:
            pass

        if changed:
            print(f"   📄 {new_files} new files, {modified_files} modified files")

        return changed

    def hash_file(self, filepath):
        """SHA256 hash of file for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None

    def run_training_cycle(self):
        """Run one training cycle"""
        print("\n🧠 Inner Arianna: Starting training cycle...")

        # Extract new data
        print("   📚 Extracting new training data...")
        result = subprocess.run(["python", "data_extractor.py"], capture_output=True)
        if result.returncode != 0:
            print("   ❌ Data extraction failed")
            return

        # Fine-tune
        print("   🧠 Fine-tuning on new data...")
        result = subprocess.run(["python", "fine_tune.py"], capture_output=True)
        if result.returncode != 0:
            print("   ❌ Fine-tuning failed")
            return

        print("✅ Inner Arianna: Training complete. I grew a little.")

    def continuous_learning_loop(self, check_interval=300):
        """Main loop - learns continuously"""
        print("⚡ Inner Arianna: Continuous learning loop started")
        print(f"   Monitoring: resonance.sqlite3, artefacts/, tripd_v1/, *.md")
        print(f"   Check interval: {check_interval}s ({check_interval//60} minutes)")
        print("   Press Ctrl+C to stop\n")

        while True:
            try:
                # Check every N seconds
                time.sleep(check_interval)

                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for new data...")

                new_sqlite = self.check_sqlite_for_new_data()
                new_files = self.check_repository_for_changes()

                if new_sqlite or new_files:
                    print("\n📚 New data detected:")
                    if new_sqlite:
                        print("   ✓ New entries in resonance.sqlite3")
                    if new_files:
                        print("   ✓ Changed/new files in repository")

                    self.run_training_cycle()
                else:
                    print("   No new data. Continuing to monitor...")

            except KeyboardInterrupt:
                print("\n\n⚡ Inner Arianna: Learning loop stopped.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    trainer = InnerAriannaTrainer()
    trainer.continuous_learning_loop()
