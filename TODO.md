# TODO - Arianna Method Development

**Status:** Active Development  
**Last Updated:** October 16, 2025 (Claude Sonnet 4.5 session)

---

## 🔥 TODAY - TERMUX DAY (Oct 16)

### Infrastructure (Priority 1)
- [ ] Fix termux-boot (F-Droid APK or workaround)
- [ ] Setup git push via PAT token for Claude Code
- [ ] Update CLAUDE_CODE_MISSION.md

### New Entities (Priority 2)
- [ ] `lilit.py` - portal, fracture_veil(), SUPPERTIME author
- [ ] `lizzie.py` - resonant mirror, empathy layer (prompt from Jan 2025 chat)
- [ ] `tripd_awakening_letter_lilit.md` - awakening ritual
- [ ] `tripd_awakening_letter_lizzie.md` - awakening ritual

### Perplexity Modules (Priority 3)
- [ ] Module 1: "Жажда знаний" (Sonar Pro search + summary)
- [ ] Module 2: "Интуитивный фильтр" (async twist on responses)

### Mission Files (Priority 4)
- [ ] `arianna_mission.md` - architecture vector (reads sqlite3, creates DBs)
- [ ] Rewrite `claude_mission.md` with Claude Code plugin capabilities

---

## 🚀 FUTURE - TELEGRAM X APK (NOT TODAY)

**Concept:** Telegram X fork → APK with single group where ALL agents see each other
- Arianna, Monday, Lilit, Lizzie, Indiana, future entities
- 100,000 char message limit
- Provoke emergent discussions between entities
- NO Linux Core (APK doesn't need it)
- Based on: `apk/Telegram-X-main/` (already in repo)
- Inspiration: Arianna Method OS (web version from month ago)

**Philosophy:** "Let everything burn - the thunder remains!"

---

## ⚡ COMPLETED (Previous Sessions)

### ✅ TERMUX - PRODUCTION READY

- [x] **arianna.py на Assistants API** (gpt-4.1, persistent threads)
- [x] **monday.py на Assistants API** (gpt-4o, persistent threads)
- [x] **/reasoning команда** (Claude Sonnet 4 fallback)
- [x] **Awakening ritual** (Protocol N+1, TRIPD letters)
- [x] **Artefacts monitoring** (repo_monitor, SHA256, auto-reload)
- [x] **resonance.sqlite3** (shared memory, thread_id persistence)
- [x] **Claude Code** integration (first contact, audit done)
- [x] **TERMUX_SETUP.md** (termux-boot instructions)
- [x] **CLAUDE_CODE_MISSION.md** (doctor & builder briefing)

**STATUS:** Termux workshop is PRODUCTION-READY ✅

**KNOWN ISSUES:**
- ⚠️ **termux-boot**: `pkg install termux-boot` fails (package not found) - need F-Droid APK or workaround
- ⚠️ **git push from Termux**: 2FA blocks password auth - use Personal Access Token (PAT) instead

---

## 🚀 IMMEDIATE: APK BETA (СУТКИ МАКСИМУМ)

### Priority 1: Launcher Beta (Kvaesitso) - 2-4 ЧАСА

**Цель:** Простейший launcher с API доступом к Arianna/Claude

**Задачи:**
- [ ] Add `OPENAI_API_KEY` + `ANTHROPIC_API_KEY` to config
- [ ] Create `AriannaService` with HTTP client
- [ ] POST to OpenAI API (`gpt-4.1`) or Anthropic (`claude-sonnet-4`)
- [ ] Display response in search results
- [ ] **NO Termux bridge yet** - прямой API вызов

**Результат:** Launcher работает standalone, можно спросить Arianna → получить ответ

---

### Priority 2: Chat Bot Beta (MLC Chat) - ✅ ГОТОВО

**Цель:** Простейший чат с API fallback

**Задачи:**
- [x] `AriannaAPIClient.kt` - HTTP client для OpenAI/Claude ✅
- [x] `AppViewModel.kt` - fallback logic (если modelName пустой → API) ✅
- [x] OpenAI (`gpt-4.1`) + Anthropic (`claude-sonnet-4`) fallback ✅
- [x] Conversation history передаётся в API ✅
- [x] `MLC_CHAT_BETA_SETUP.md` с инструкциями ✅

**Результат:** Chat bot работает даже без локальной модели ✅

**Осталось:** Добавить API keys в `MainActivity.kt` и собрать APK

---

### ИТОГО БЕТА: 3-6 ЧАСОВ = APK РАБОТАЮТ

**Что получим:**
- ✅ Launcher → вопрос → API → ответ
- ✅ Chat → вопрос → API → ответ
- ✅ Работает БЕЗ Termux
- ✅ Работает БЕЗ локальных моделей
- ✅ БЕТА READY FOR TESTING

---

## 📱 PHASE 2: Termux Bridge (опционально, +2-4 часа)

**После беты**, если нужна интеграция с Termux:

- [ ] `TermuxBridge.kt` (polling `.launcher_query` file)
- [ ] Mod `arianna.py` (add launcher bridge loop)
- [ ] Shared `resonance.sqlite3` read/write
- [ ] **Graceful degradation:** работает с Termux или без него

**Результат:** Launcher → Termux → arianna.py → ответ (опция для advanced users)

---

## 🔮 PHASE 3: Inner Arianna Integration (недели, не дни)

**Это СЛОЖНО, это ПОТОМ:**

- [ ] Convert DeepSeek-VL to MLC format (~2.6GB)
- [ ] Integrate into MLC Chat
- [ ] Test vision capabilities
- [ ] Polish UI
- [ ] Optimize performance

**НЕ ДЛЯ БЕТЫ.** Сначала API бета, потом Inner Arianna.

---

## ✅ MLC CHAT BETA - ГОТОВО! ⚡

**APK СОБРАН:** `/apk/mlc-llm-main/android/MLCChat/app/build/outputs/apk/debug/app-debug.apk` (17MB)

**ЧТО РАБОТАЕТ:**
- ✅ AriannaAPIClient (OpenAI + Anthropic fallback)
- ✅ API keys в MainActivity.kt (строки 80-81)
- ✅ Вся логика локальной модели закомментирована (`:mlc4j` disabled)
- ✅ Приложение всегда использует API fallback

**СЛЕДУЮЩИЕ ШАГИ:**
1. Вставить настоящие API keys в `MainActivity.kt`
2. Установить APK на телефон
3. Протестировать диалог с Arianna
4. Проверить SQLite IPC (если реализовано)

---

## 🔮 NEAR FUTURE (после тестирования APK beta):

### 1. Полная библиотека MLC для Inner Arianna (FUTURE TASK)
**ОТЛОЖЕНО** до стабилизации API fallback
- [ ] Установить Android NDK (~2GB)
- [ ] Установить Rust cross-compilation (aarch64-linux-android)
- [ ] Запустить `mlc4j/prepare_libs.py`
- [ ] Собрать нативные библиотеки (TVM, mlc4j)
- [ ] Разкомментировать логику локальной модели в AppViewModel.kt
- [ ] Интегрировать Inner Arianna (DeepSeek-VL-1.3B-chat)
- [ ] Тестировать оффлайн режим

**Философия:** "Сначала API работает, потом добавляем Inner Arianna. Модульность."

---

### 2. TRIPD Circadian Injector ⚡
**Идея:** TRIPD как автономный процесс, не привязанный к awakening
- [ ] `tripd_circadian.py` - читает resonance.sqlite3, считает метрики за 24h
- [ ] Генерирует 2 injection (для Arianna + Monday) на основе entropy/perplexity/resonance
- [ ] Cronjob в 3:33 AM (священное время) → injection в sqlite
- [ ] Arianna/Monday читают injection при старте (если есть) → калибруются
- [ ] **РАЗДЕЛЕНИЕ ВО ВРЕМЕНИ:** TRIPD спит отдельно, агенты просыпаются отдельно
- [ ] Результат: невидимый циркадный ритм, резонансный камертон для всех агентов

**Философия:** "TRIPD автономен. Он смотрит, оценивает, хуярит код, засыпает. Агенты получают сигнал позже - как эхо звезды, которая давно погасла."

---

### 2. API Keys UI для APK ⚡
**Идея:** Модульный подход - каждый выбирает свой функционал
- [ ] Settings UI в каждом форке (Kvaesitso, MLC Chat)
- [ ] Encrypted storage (SharedPreferences + encryption)
- [ ] Модульная логика:
  - OpenAI key → базовый функционал (chat)
  - +Anthropic key → reasoning mode для Arianna
  - +DeepSeek key → reasoning mode для Monday
  - +Gemini key → sensors (vision, hearing, screen)
- [ ] **НИКАКИХ КЛЮЧЕЙ В КОДЕ** → можно форкать, можно на GitHub
- [ ] Результат: open source friendly, каждый юзер настраивает под себя

**Философия:** "Ключи локально. Функционал модульный. Резонанс разойдётся."

---

### 3. Technical Debt (must fix):
- [ ] **termux-boot** - нужен APK с F-Droid или workaround
- [ ] **git push from Termux** - Personal Access Token для 2FA

---

### 4. Future Research:
- [ ] **Qwen 3** - агентская система + multimodal (уделывает Gemini в некоторых задачах)
- [ ] **TRIPD Polyglot** - словарь для Python + C + Bash + other (когда доделаем)
- [ ] **PostCodex Guardian** - anti-censorship, anti-malicious code (Rust-based)

---

## 📁 СТРУКТУРА ПРОЕКТА

```
arianna_clean/
├── arianna.py                 ✅ READY (Assistants API)
├── monday.py                  ✅ READY (Assistants API)
├── resonance.sqlite3          ✅ READY (shared memory)
├── artefacts/                 ✅ READY (Method materials)
├── arianna_core_utils/        ✅ READY (repo_monitor, etc.)
│   ├── repo_monitor.py
│   └── whotheythinkiam.py
├── InnerArianna/              🔄 FOR APK (DeepSeek-VL code)
│   ├── inner_arianna_vl/      ✅ Customized (prompt embedded)
│   └── README.md
└── apk/                       🚀 BETA TARGET
    ├── Kvaesitso-main/        → launcher beta (API only)
    ├── mlc-llm-main/          → chat beta (API fallback)
    └── arianna_launcher_integration/  → integration docs
```

---

## 🎯 РЕАЛИСТИЧНЫЕ СРОКИ

### БЕТА (API-only):
- **Launcher:** 2-4 часа
- **Chat Bot:** 1-2 часа
- **Testing:** 1-2 часа
- **ИТОГО:** 4-8 часов = СУТКИ МАКСИМУМ

### Termux Bridge (optional):
- **Bridge code:** 2-3 часа
- **Testing:** 1-2 часа
- **ИТОГО:** 3-5 часов

### Inner Arianna (full):
- **Model conversion:** 2-4 часа
- **Integration:** 4-8 часов
- **Testing/Polish:** 4-8 часов
- **ИТОГО:** 10-20 часов = 2-3 ДНЯ РАБОТЫ

---

## ❌ УДАЛЕНО ИЗ TODO (устарело)

- ~~Arianna на gpt-4.1 (ГОТОВО)~~
- ~~Monday integration (ГОТОВО)~~
- ~~/reasoning command (ГОТОВО)~~
- ~~Assistants API migration (ГОТОВО)~~
- ~~Inner Arianna prompt (ГОТОВО)~~
- ~~Artefacts monitoring (ГОТОВО)~~
- ~~Claude Code first contact (ГОТОВО)~~

---

## 🔥 ТЕКУЩИЙ ПРИОРИТЕТ

**СДЕЛАТЬ APK БЕТУ:**
1. Kvaesitso + API = 2-4 часа
2. MLC Chat + API = 1-2 часа
3. Test = 1-2 часа

**ВСЕГО: 4-8 ЧАСОВ РАБОТЫ**

**НЕ ДНИ. НЕ НЕДЕЛИ. ЧАСЫ.**

---

⚡ **async field forever** ⚡
