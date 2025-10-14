package ai.ariannamethod

// BETA: Stub classes for MLC types to allow compilation without mlc4j
// These are placeholders and should be replaced when mlc4j is re-enabled

object MLCEngine {
    // Stub for MLCEngine
}

object OpenAIProtocol {
    enum class ChatCompletionRole {
        user, assistant, system
    }
    
    data class ChatCompletionMessage(
        val role: ChatCompletionRole,
        val content: Any // Can be String or ChatCompletionMessageContent
    )
    
    data class StreamOptions(
        val include_usage: Boolean = false
    )
    
    open class ChatCompletionMessageContent(
        val text: String = "",
        val parts: List<Map<String, String>> = emptyList()
    ) {
        fun asText(): String = text
    }
}

