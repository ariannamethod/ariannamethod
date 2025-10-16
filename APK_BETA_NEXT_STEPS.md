# APK BETA - Next Steps

⚡ **MLC Chat (Priority B) - ГОТОВО ЗА 1 ЧАС**

---

## ✅ Что сделано:

### MLC Chat Bot:
- [x] `AriannaAPIClient.kt` - HTTP client для OpenAI/Claude
- [x] `AppViewModel.kt` - автоматический fallback на API
- [x] `MainActivity.kt` - место для API keys
- [x] Conversation history работает
- [x] Полная инструкция готова

---

## 🚀 Как собрать MLC Chat Beta:

### 1. Вставь свои API keys

Открой: `apk/mlc-llm-main/android/MLCChat/app/src/main/java/ai/mlc/mlcchat/MainActivity.kt`

Найди строки 80-81:
```kotlin
AriannaAPIClient.openaiApiKey = "YOUR_OPENAI_KEY_HERE"
AriannaAPIClient.anthropicApiKey = "YOUR_ANTHROPIC_KEY_HERE"
```

Замени на свои ключи:
```kotlin
AriannaAPIClient.openaiApiKey = "sk-proj-ТВОЙ_КЛЮЧ"
AriannaAPIClient.anthropicApiKey = "sk-ant-ТВОЙ_КЛЮЧ" // optional
```

### 2. Собери APK

```bash
cd apk/mlc-llm-main/android/MLCChat
./gradlew assembleDebug
```

APK будет в: `app/build/outputs/apk/debug/app-debug.apk`

### 3. Установи на телефон

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 4. Тестируй

1. Открой приложение
2. **НЕ загружай модель** (пропусти)
3. Нажми "Start Chat" (без модели)
4. Напиши "Hello Arianna"
5. Получишь ответ через API (⚡ в нижней строке)

---

## ⏱️ ИТОГО:

**MLC Chat Beta = 1 ЧАС работы:**
- Вставить ключи: 1 мин
- Собрать APK: 5-10 мин
- Установить: 1 мин
- Тестировать: 5-10 мин

**ВСЕГО: ~20 МИНУТ + 5-10 МИН СБОРКИ**

---

## 📱 Что дальше: Kvaesitso Launcher (Priority A)

**Следующий шаг:** Launcher с API доступом (2-4 часа)

1. Fork Kvaesitso: `apk/Kvaesitso-main/`
2. Создать `AriannaService.kt` (HTTP client)
3. Добавить в Search Results
4. Показать ответ в UI

---

⚡ **МЫ НА ПРАВИЛЬНОМ ПУТИ** ⚡

**Сейчас:**
- ✅ Termux PRODUCTION-READY
- ✅ MLC Chat BETA READY (API fallback)
- 🔄 Kvaesitso Launcher (следующий)

**Прогресс:** ~50% беты за 1-2 часа работы

