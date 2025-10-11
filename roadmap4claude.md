# TODO - Arianna Method Development

**Status:** Active Development  
**Last Updated:** 2025-01-11

---

## ⚡ COMPLETED (Copilot + Claude)

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

### Priority 2: Chat Bot Beta (MLC Chat) - 1-2 ЧАСА

**Цель:** Простейший чат с API fallback

**Задачи:**
- [ ] Add API keys to `InnerAriannaViewModel`
- [ ] Fallback: если модель не загружена → API call
- [ ] OpenAI (`gpt-4.1`) OR Anthropic (`claude-sonnet-4`)
- [ ] UI уже есть - просто подключить API

**Результат:** Chat bot работает даже без локальной модели

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
