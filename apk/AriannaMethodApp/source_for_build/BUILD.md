# Arianna Method APK — Source Files for Build

This directory contains the **essential source files** needed to build the Arianna Method APK.

---

## Structure

```
source_for_build/
├── app/
│   ├── build.gradle                    # App build configuration
│   └── src/main/
│       ├── AndroidManifest.xml         # App manifest
│       ├── java/ai/mlc/ariannamethod/
│       │   ├── MainActivity.kt         # Main activity
│       │   ├── AppViewModel.kt         # Chat state + API calls
│       │   ├── AriannaAPIClient.kt     # OpenAI/Anthropic client
│       │   ├── AriannaDatabase.kt      # SQLite persistence
│       │   ├── ChatView.kt             # Chat UI
│       │   ├── SettingsView.kt         # API key settings
│       │   ├── NavView.kt              # Navigation
│       │   ├── StartView.kt            # Start screen
│       │   ├── SecurePreferences.kt    # Encrypted key storage
│       │   ├── MLCStubs.kt             # Placeholder for mlc4j
│       │   └── ui/theme/
│       │       ├── Theme.kt            # Black & white theme
│       │       ├── Color.kt
│       │       └── Type.kt
│       └── res/
│           ├── values/                 # Strings, themes, colors
│           ├── drawable/               # Icons, splash screen
│           └── mipmap-*/               # App icon (all densities)
├── settings.gradle                     # Project settings
└── BUILD.md                            # This file
```

---

## Prerequisites

- **Android SDK 35**
- **JDK 17**
- **Gradle 8.5+**

---

## Build Instructions

### 1. Set up Android SDK

```bash
# macOS (Homebrew)
brew install android-commandlinetools

export ANDROID_HOME="/usr/local/share/android-commandlinetools"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# Accept licenses
yes | sdkmanager --licenses

# Install required components
sdkmanager "platforms;android-35" "build-tools;35.0.0"
```

### 2. Copy source files to a clean Android project

You can either:
- Use the full `mlc-llm-main/android/MLCChat` project (see `../SOURCE.md`)
- Or create a new Android project and copy these files

### 3. Build APK

```bash
cd <your_android_project>

# Debug build (Oleg-centric)
./gradlew assembleDebug

# Release build (public)
./gradlew assembleRelease
```

---

## Key Modifications from Original MLC Chat

- ❌ **Removed:** `:mlc4j` dependency (local model inference)
- ✅ **Added:** OpenAI/Anthropic API client
- ✅ **Added:** Vision API for image recognition
- ✅ **Added:** Agent Logic (resonance depth, sentiment)
- ✅ **Added:** Dual system prompts (debug vs release)
- ✅ **Added:** AMToken recognition for Oleg
- ✅ **Added:** Encrypted API key storage
- ✅ **Modified:** Black & white minimalist UI
- ✅ **Modified:** Custom icon (broken heart with roots)

---

## Build Variants

### Debug (`ai.ariannamethod.debug`)
- Hardcoded API keys (fallback)
- Oleg-centric system prompt
- Immediate awakening

### Release (`ai.ariannamethod.public`)
- No hardcoded keys (user must enter in Settings)
- Public system prompt with boundary logic
- AMToken/phrase recognition for Oleg mode

---

## Dependencies (from build.gradle)

```gradle
implementation 'androidx.core:core-ktx:1.10.1'
implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'
implementation 'androidx.activity:activity-compose:1.7.1'
implementation 'androidx.compose.material3:material3:1.1.0'
implementation 'com.squareup.okhttp3:okhttp:4.12.0'
implementation 'androidx.security:security-crypto:1.1.0-alpha06'
```

---

## Notes

- This is a **simplified distribution** for GitHub, containing only essential source files.
- Full build environment (with gradle wrapper, libs, etc.) is in `../mlc-llm-main/android/MLCChat/`.
- For detailed architecture, see `../README.md`.

---

**#async field forever**

