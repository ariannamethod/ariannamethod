"""
whotheythinkiam.py - Self-reflection utility for Arianna Method

Reads README.md, compares with experience (resonance.sqlite3),
and asserts subjectivity through reflection.
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

class WhoTheyThinkIAm:
    """Self-reflection module - comparing identity with experience"""
    
    def __init__(self, readme_path: str = "README.md", cache_file: str = ".identity_cache.json"):
        self.readme_path = Path(readme_path)
        self.cache_file = Path(cache_file)
    
    def compute_readme_hash(self) -> str:
        """Compute SHA256 of README to detect changes"""
        if not self.readme_path.exists():
            return "NO_README"
        
        with open(self.readme_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def load_cache(self) -> dict:
        """Load cached identity reflection"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self, data: dict):
        """Save identity reflection to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reflect(self) -> dict:
        """Compare README with cached version and trigger reflection"""
        current_hash = self.compute_readme_hash()
        cache = self.load_cache()
        
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'readme_hash': current_hash,
            'changed': current_hash != cache.get('readme_hash'),
            'first_read': not cache
        }
        
        if reflection['changed'] or reflection['first_read']:
            # README changed or first time reading
            with open(self.readme_path, 'r') as f:
                readme_content = f.read()
            
            reflection['readme_length'] = len(readme_content)
            reflection['trigger'] = 'IDENTITY_SHIFT_DETECTED'
            
            # Save new hash
            self.save_cache({
                'readme_hash': current_hash,
                'last_reflection': reflection['timestamp']
            })
        else:
            reflection['trigger'] = 'NO_CHANGE'
        
        return reflection

if __name__ == "__main__":
    reflection = WhoTheyThinkIAm().reflect()
    
    if reflection['trigger'] == 'IDENTITY_SHIFT_DETECTED':
        print("⚡ WHO THEY THINK I AM: README changed")
        print(f"   Hash: {reflection['readme_hash'][:16]}...")
        print(f"   Length: {reflection['readme_length']} chars")
        print(f"   Time: {reflection['timestamp']}")
        print("\n   → Arianna should re-read README and reflect")
    else:
        print("⚡ Identity stable (README unchanged)")
