# Arianna Launcher Integration

Integration files for forking Kvaesitso → arianna-launcher

---

## 📁 Files

```
arianna_launcher_integration/
├── INTEGRATION_PLAN.md    # Full architecture & implementation plan
├── AriannaItem.kt          # UI component (Compose)
├── TermuxBridge.kt         # IPC with Termux (SQLite-based)
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Fork Kvaesitso

```bash
cd /Users/ataeff/Downloads/arianna_clean/apk
mv Kvaesitso-main arianna-launcher
cd arianna-launcher

# Rename package (find & replace in all files)
# de.mm20.launcher2 → com.ariannamethod.launcher
```

### 2. Add Arianna Module

```bash
mkdir -p app/ui/src/main/java/com/ariannamethod/launcher/ui/launcher/search/arianna
mkdir -p services/arianna/src/main/java/com/ariannamethod/launcher/services/arianna
```

**Copy files:**
- `AriannaItem.kt` → `app/ui/src/main/java/.../search/arianna/`
- `TermuxBridge.kt` → `services/arianna/src/main/java/.../services/arianna/`

### 3. Modify SearchColumn.kt

**Location:** `app/ui/src/main/java/.../ui/launcher/search/SearchColumn.kt`

**Add Arianna section:**

```kotlin
// After existing results sections
if (searchQuery.isNotEmpty()) {
    AriannaResults(
        searchQuery = searchQuery,
        viewModel = ariannaVM
    )
}
```

### 4. Add Termux Bridge Integration

**In Termux (`arianna.py`)**, add launcher bridge:

```python
async def launcher_bridge():
    """Poll for queries from launcher"""
    trigger_file = Path.home() / "ariannamethod" / ".launcher_query"
    
    while True:
        if trigger_file.exists():
            query = trigger_file.read_text()
            trigger_file.unlink()
            
            response = await self.think(query)
            save_to_memory(response, context="arianna_response")
        
        await asyncio.sleep(0.5)

# In main():
asyncio.create_task(launcher_bridge())
```

### 5. Build & Test

```bash
cd arianna-launcher
./gradlew assembleDebug

# Install APK
adb install -r app/app/build/outputs/apk/debug/app-debug.apk

# Test: Type in search bar, should trigger Arianna
```

---

## 🔌 Communication Flow

```
┌─────────────────┐
│ User types      │
│ in search bar   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│ AriannaItem detects     │
│ "@arianna" trigger or   │
│ certain keywords        │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│ TermuxBridge writes to: │
│ .launcher_query file    │
└────────┬────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Termux arianna.py polls  │
│ file, processes query    │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Response written to:     │
│ resonance.sqlite3        │
│ context='arianna_response'│
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ TermuxBridge polls DB,   │
│ retrieves response       │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ AriannaItem displays     │
│ response in launcher     │
└──────────────────────────┘
```

---

## 🎨 UI Customization

### Change Icon

Replace default icon with Arianna's:

**Location:** `app/app/src/main/res/mipmap-*/ic_launcher.png`

Use ⚡ or custom Arianna logo.

### Change Colors

**Location:** `app/ui/src/main/res/values/colors.xml`

```xml
<color name="arianna_primary">#7B2CBF</color>  <!-- Electric purple -->
<color name="arianna_secondary">#5A189A</color>
<color name="inner_arianna">#3C096C</color>  <!-- Deeper, indigo -->
```

### Change App Name

**Location:** `app/app/src/main/res/values/strings.xml`

```xml
<string name="app_name">Arianna</string>
```

---

## 🔥 Advanced: Sensor Integration

### Add Gemini API

**New file:** `services/arianna/src/main/java/.../GeminiSensorService.kt`

```kotlin
class GeminiSensorService(private val apiKey: String) {
    
    suspend fun analyzeImage(uri: Uri): String {
        // Gemini vision API call
    }
    
    suspend fun transcribeAudio(uri: Uri): String {
        // Gemini audio API call
    }
}
```

**Permissions (AndroidManifest.xml):**

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

**Usage in launcher:**

```kotlin
// When user types "@see" → open camera
if (query.startsWith("@see")) {
    val imageUri = launchCamera()
    val analysis = geminiService.analyzeImage(imageUri)
    // Send to Arianna with context
}
```

---

## 📝 TODO

- [ ] Fork Kvaesitso
- [ ] Rename package
- [ ] Add Arianna module
- [ ] Integrate TermuxBridge
- [ ] Test basic query/response
- [ ] Add Gemini sensors
- [ ] Integrate Inner Arianna (when chat APK found)
- [ ] Polish UI
- [ ] Add voice input
- [ ] Add shortcuts for Main/Inner toggle

---

⚡ **The launcher becomes the body. Termux remains the mind.** ⚡

