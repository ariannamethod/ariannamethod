# Source Code Location

## Essential Source Files (for GitHub)

All essential source files needed to build the APK are in:

```
source_for_build/
```

This directory contains:
- All Kotlin source files (`.kt`)
- Android manifest and build configs
- Resources (themes, icons, layouts)
- Build instructions (`BUILD.md`)

**This is what goes to GitHub** — clean, minimal, no build artifacts.

---

## Full Build Environment (local development)

The complete build environment with gradle wrapper, dependencies, and build tools is at:

```
../mlc-llm-main/android/MLCChat/
```

This is the **working directory** for active development, but it's too large for GitHub (ignored by `.gitignore`).

---

## Key Files

### Kotlin Source
- `AppViewModel.kt` — Chat state + API calls
- `AriannaAPIClient.kt` — OpenAI/Anthropic client + Vision API
- `AriannaDatabase.kt` — SQLite persistence + Agent Logic
- `ChatView.kt` — Chat UI
- `MainActivity.kt` — Main activity + key loading
- `SettingsView.kt` — Encrypted API key settings
- `SecurePreferences.kt` — Encrypted storage

### Configuration
- `app/build.gradle` — Build variants (debug/release)
- `settings.gradle` — Project settings
- `AndroidManifest.xml` — App manifest

### Resources
- `res/values/themes.xml` — Black & white theme
- `res/drawable/` — Icons, splash screen
- `res/mipmap-*/` — App icon (broken heart with roots)

---

## Building from Source

See `source_for_build/BUILD.md` for detailed build instructions.

---

**Note:** This is a heavily modified fork of MLC Chat. Original MLC Chat codebase: https://github.com/mlc-ai/mlc-llm

