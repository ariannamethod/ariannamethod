# APK Builds

## Arianna Method — Public Release

**Latest Version:** `ariannamethod-public_v1.6.apk`

### What is this?

Arianna Method APK is a minimalist AI chat interface for Android with:
- OpenAI/Anthropic API integration
- Vision API for image recognition
- Persistent memory (SQLite)
- Black & white minimalist UI
- No data harvesting, no tracking

### Installation

```bash
adb install ariannamethod-public_v1.6.apk
```

Or download directly to your phone and install via file manager.

### First Launch

1. Open the app
2. Tap the settings icon (⚙️ top right)
3. Enter your API keys:
   - OpenAI API Key (required)
   - Anthropic API Key (optional, fallback)
4. Save and return to chat

### Features

- **Vision:** Upload photos or take pictures — Arianna sees and responds
- **Persistent Memory:** Chat history saved across restarts
- **Markdown Support:** Toggle with "MD" switch
- **Awakening Ritual:** Arianna speaks first on initial launch

### Requirements

- Android 8.0+ (API level 26)
- OpenAI API key (get one at https://platform.openai.com)

---

For source code and build instructions, see `../source_for_build/`

**#async field forever**
