# MLC Chat - Arianna API Beta

⚡ **БЕТА-ВЕРСИЯ с API fallback**

## Что сделано:

✅ `AriannaAPIClient.kt` - HTTP client для OpenAI/Claude  
✅ `AppViewModel.kt` - автоматический fallback на API если модель не загружена  
✅ Conversation history сохраняется и передаётся в API  

---

## Как настроить:

### 1. Добавь API ключи

Открой `MainActivity.kt` и добавь в `onCreate()`:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    // ⚡ BETA: Set API keys for fallback
    AriannaAPIClient.openaiApiKey = "sk-proj-..." // OpenAI key
    AriannaAPIClient.anthropicApiKey = "sk-ant-..." // Claude key (optional)
    
    // ... rest of code
}
```

### 2. Собери APK

```bash
cd android/MLCChat
./gradlew assembleDebug
```

APK будет в: `app/build/outputs/apk/debug/app-debug.apk`

### 3. Установи на телефон

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## Как работает:

### БЕЗ локальной модели:
1. Открываешь приложение
2. Не загружаешь модель (пропускаешь)
3. Начинаешь чат
4. **Автоматически используется OpenAI API (gpt-4.1)**
5. Если OpenAI недоступен → **Fallback на Claude (Sonnet 4)**

### С локальной моделью:
1. Загружаешь модель (DeepSeek-VL или другую)
2. Начинаешь чат
3. **Используется локальная модель**
4. API не вызывается

---

## Что дальше:

- [ ] Переместить API keys в Settings UI (не хардкодить)
- [ ] Добавить индикатор "API mode" vs "Local model"
- [ ] Streaming responses для API (сейчас весь ответ сразу)
- [ ] Vision support через API (OpenAI GPT-4 Vision)
- [ ] Интеграция с Inner Arianna (DeepSeek-VL локально)

---

## Тестирование:

1. **Без модели:**
   - Открой приложение
   - Не загружай модель
   - Start Chat
   - Напиши "Hello Arianna"
   - Должен прийти ответ через API (⚡ в нижней строке)

2. **С моделью:**
   - Загрузи модель
   - Start Chat
   - Напиши вопрос
   - Должна работать локальная модель

---

⚡ **БЕТА ГОТОВА ЗА 1-2 ЧАСА** ⚡

