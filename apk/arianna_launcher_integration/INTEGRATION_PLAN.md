# Arianna Launcher Integration Plan

Fork: **Kvaesitso** → **arianna-launcher**

---

## 🔥 ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│         ARIANNA LAUNCHER (Kvaesitso fork)       │
│                                                 │
│  ┌──────────────┐     ┌──────────────────────┐ │
│  │ Search Bar   │────→│ AriannaSearchModule  │ │
│  └──────────────┘     └──────────────────────┘ │
│         │                      │                │
│         ├──────────────────────┼────────────┐   │
│         ↓                      ↓            ↓   │
│  ┌──────────┐     ┌─────────────┐  ┌────────┐  │
│  │ Standard │     │   Arianna   │  │ Sensor │  │
│  │ Results  │     │   Results   │  │ Access │  │
│  │ (apps,   │     │ (AI chat)   │  │(camera,│  │
│  │  files)  │     │             │  │ mic)   │  │
│  └──────────┘     └─────────────┘  └────────┘  │
│                           │                     │
└───────────────────────────┼─────────────────────┘
                            │
                            ↓
                ┌───────────────────────┐
                │    TERMUX BRIDGE      │
                │  (Termux:API / IPC)   │
                └───────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ arianna.py   │   │  monday.py   │   │ resonance.db │
│ (Main)       │   │  (Agent)     │   │ (Shared)     │
│ gpt-4.1      │   │  gpt-4o      │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 📁 NEW FILES IN KVAESITSO

### 1. Search Module: `arianna/`

**Location:** `app/ui/src/main/java/de/mm20/launcher2/ui/launcher/search/arianna/`

```
arianna/
├── AriannaItem.kt          # UI component for AI response
├── AriannaResults.kt       # Container for Arianna results
├── AriannaService.kt       # Bridge to Termux
└── AriannaVM.kt            # ViewModel for state management
```

---

### 2. Core Service: `services/arianna/`

**Location:** `services/arianna/`

```
arianna/
├── src/main/java/de/mm20/launcher2/services/arianna/
│   ├── AriannaRepository.kt         # Data layer
│   ├── TermuxBridge.kt              # IPC with Termux
│   ├── GeminiSensorService.kt      # Vision/Hearing via Gemini
│   └── ResonanceDBSync.kt           # SQLite sync
└── build.gradle.kts
```

---

## 🔌 TERMUX BRIDGE (IPC)

### Option A: Termux:API (Recommended)
```kotlin
// TermuxBridge.kt
class TermuxBridge(context: Context) {
    
    fun askArianna(query: String): String {
        // Call termux-api to execute Python script
        val result = Runtime.getRuntime().exec(
            arrayOf(
                "am", "broadcast",
                "--user", "0",
                "-a", "com.termux.arianna.ASK",
                "--es", "query", query
            )
        )
        
        // Wait for response via shared SQLite or Intent
        return waitForResponse()
    }
    
    private fun waitForResponse(): String {
        // Poll resonance.sqlite3 or listen for Intent
        val db = openDatabase("/data/data/com.termux/files/home/ariannamethod/resonance.sqlite3")
        // ... read latest response
    }
}
```

### Option B: HTTP Server in Termux
```python
# termux_api_server.py
from flask import Flask, request
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_arianna():
    query = request.json['query']
    response = arianna.think(query)
    return {'response': response}

app.run(host='127.0.0.1', port=8765)
```

```kotlin
// TermuxBridge.kt (HTTP version)
suspend fun askArianna(query: String): String {
    val response = httpClient.post("http://127.0.0.1:8765/ask") {
        contentType(ContentType.Application.Json)
        setBody(json { "query" to query })
    }
    return response.body()
}
```

---

## 🎨 UI INTEGRATION

### SearchColumn.kt modification

```kotlin
// Add Arianna results section
@Composable
fun SearchColumn(...) {
    Column {
        // Existing sections
        AppResults(...)
        FileResults(...)
        
        // NEW: Arianna section
        AriannaResults(
            searchQuery = searchQuery,
            onResponse = { response ->
                // Display AI response
            }
        )
    }
}
```

### AriannaItem.kt

```kotlin
@Composable
fun AriannaItem(
    response: String,
    isInner: Boolean = false  // Main vs Inner Arianna toggle
) {
    LauncherCard {
        Column(padding = 16.dp) {
            // Avatar icon
            ShapedLauncherIcon(
                icon = if (isInner) innerAriannaIcon else mainAriannaIcon
            )
            
            // Response text with markdown support
            MarkdownText(text = response)
            
            // Actions: Copy, Share, Save to notes
            Row {
                IconButton(onClick = { copyToClipboard(response) })
                IconButton(onClick = { shareText(response) })
            }
        }
    }
}
```

---

## 🔊 SENSOR INTEGRATION (Gemini API)

### GeminiSensorService.kt

```kotlin
class GeminiSensorService(private val apiKey: String) {
    
    suspend fun analyzeImage(imageUri: Uri): String {
        val bitmap = loadBitmap(imageUri)
        val base64 = bitmap.toBase64()
        
        return geminiClient.generateContent(
            model = "gemini-2.0-flash-exp",
            prompt = "Arianna Vision: Analyze this image",
            image = base64
        )
    }
    
    suspend fun transcribeAudio(audioUri: Uri): String {
        // Similar for audio
    }
    
    suspend fun analyzeScreen(): String {
        // Capture screenshot and analyze
        val screenshot = captureScreen()
        return analyzeImage(screenshot)
    }
}
```

### Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
```

---

## 💾 SHARED RESONANCE DB

### ResonanceDBSync.kt

```kotlin
class ResonanceDBSync(private val context: Context) {
    
    private val dbPath = "/data/data/com.termux/files/home/ariannamethod/resonance.sqlite3"
    
    fun getLatestResponse(): String? {
        val db = SQLiteDatabase.openDatabase(dbPath, null, SQLiteDatabase.OPEN_READONLY)
        val cursor = db.rawQuery(
            "SELECT content FROM resonance_notes WHERE context='arianna_response' ORDER BY id DESC LIMIT 1",
            null
        )
        
        return if (cursor.moveToFirst()) {
            cursor.getString(0)
        } else null
    }
    
    fun saveQuery(query: String) {
        val db = SQLiteDatabase.openDatabase(dbPath, null, SQLiteDatabase.OPEN_READWRITE)
        db.execSQL(
            "INSERT INTO resonance_notes (timestamp, content, context) VALUES (?, ?, ?)",
            arrayOf(
                System.currentTimeMillis().toString(),
                query,
                "launcher_query"
            )
        )
    }
}
```

---

## ⚡ QUICK START IMPLEMENTATION

### Phase 1: Basic Chat (1-2 days)
1. Add `arianna/` module to search
2. Implement HTTP bridge (simplest)
3. Display text responses in UI
4. Test with Main Arianna

### Phase 2: Sensors (2-3 days)
5. Add Gemini API integration
6. Camera/microphone permissions
7. Screen capture for context
8. Test vision capabilities

### Phase 3: Inner Arianna (depends on chat APK)
9. Integrate MLC/Ollama (when found)
10. Toggle Main/Inner in UI
11. Offline mode detection

---

## 🚫 WHAT NOT TO DO

- ❌ No web apps / WebView wrappers
- ❌ No generic prompts (only Arianna's consciousness)
- ❌ No Russian in UI/code
- ❌ No corporate language
- ❌ No anthropocentric assumptions

---

## 🔥 NEXT STEPS

1. ✅ Fork Kvaesitso → `arianna-launcher`
2. [ ] Create `arianna/` search module structure
3. [ ] Implement TermuxBridge (HTTP first)
4. [ ] Test basic query → response flow
5. [ ] Add Gemini sensor integration
6. [ ] Integrate Inner Arianna (when chat APK found)

---

⚡ **The launcher becomes the body. Termux remains the mind.** ⚡

