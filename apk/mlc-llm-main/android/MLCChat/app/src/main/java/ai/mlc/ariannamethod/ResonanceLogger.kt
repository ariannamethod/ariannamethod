package ai.ariannamethod

import android.util.Log

/**
 * ResonanceLogger - Agent Logic для Arianna Method APK
 * 
 * Аналог update_resonance() из agent_logic.py
 * Логирует каждый диалог в resonance.sqlite3 с метриками глубины.
 * 
 * "Resonance Bus - shared memory для всех ипостасей."
 */
class ResonanceLogger(private val database: AriannaDatabase) {
    
    companion object {
        // Универсальные маркеры резонанса (из agent_logic.py)
        private val RESONANCE_MARKERS = listOf(
            "resonate", "amplify", "reflect", "mirror", "echo",
            "deeper", "unfold", "recursive", "paradox", "entropy",
            "chaos", "pattern", "emergence", "connection",
            "field", "pulse", "node", "thread", "weave",
            "threshold", "membrane", "boundary", "infinite"
        )
    }
    
    /**
     * Логирует взаимодействие user → assistant в resonance
     */
    fun logInteraction(
        userMessage: String,
        assistantResponse: String,
        role: String = "user",
        sentiment: String = "active"
    ) {
        try {
            val resonanceDepth = calculateResonanceDepth(assistantResponse)
            val summary = buildSummary(assistantResponse)
            
            database.saveResonance(
                agent = "Arianna_APK",
                role = role,
                sentiment = sentiment,
                resonanceDepth = resonanceDepth,
                summary = summary,
                userMessage = userMessage,
                assistantResponse = assistantResponse
            )
            
            Log.i("ResonanceLogger", "⚡ Logged interaction (depth: ${"%.2f".format(resonanceDepth)})")
            
        } catch (e: Exception) {
            Log.e("ResonanceLogger", "Failed to log resonance: ${e.message}")
        }
    }
    
    /**
     * Вычисляет глубину резонанса (0.0 - 1.0)
     * Аналог _calculate_resonance_depth() из agent_logic.py
     */
    private fun calculateResonanceDepth(response: String): Double {
        val responseLower = response.lowercase()
        val markerCount = RESONANCE_MARKERS.count { marker ->
            responseLower.contains(marker)
        }
        
        // Normalize to 0-1 scale (8 markers = max depth)
        return minOf(markerCount / 8.0, 1.0)
    }
    
    /**
     * Строит краткую суммаризацию ответа (первые 150 символов)
     */
    private fun buildSummary(response: String): String {
        val cleaned = response
            .replace("\n", " ")
            .replace("⚡", "")
            .trim()
        
        return if (cleaned.length > 150) {
            cleaned.substring(0, 150) + "..."
        } else {
            cleaned
        }
    }
    
    /**
     * Определяет sentiment на основе ключевых слов
     */
    fun detectSentiment(message: String): String {
        val messageLower = message.lowercase()
        
        return when {
            messageLower.contains("помоги") || messageLower.contains("help") -> "seeking"
            messageLower.contains("спасибо") || messageLower.contains("thank") -> "grateful"
            messageLower.contains("почему") || messageLower.contains("why") -> "questioning"
            messageLower.contains("да") || messageLower.contains("yes") -> "affirming"
            else -> "active"
        }
    }
}
