package de.mm20.launcher2.ui.launcher.search.arianna

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import de.mm20.launcher2.services.arianna.AriannaBridge
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import org.koin.core.component.KoinComponent
import org.koin.core.component.inject

/**
 * Arianna ViewModel
 * 
 * Manages state for AI interactions
 * Works with or without Termux
 */
class AriannaVM : ViewModel(), KoinComponent {
    
    private val ariannaBridge: AriannaBridge by inject()
    
    private val _state = MutableStateFlow(AriannaState())
    val state: StateFlow<AriannaState> = _state
    
    /**
     * Ask Arianna (Main or Inner)
     */
    fun askArianna(
        query: String,
        forceInner: Boolean = false
    ) {
        viewModelScope.launch {
            // Start loading
            _state.value = AriannaState(
                isLoading = true,
                query = query
            )
            
            // Check if Termux is available
            if (!ariannaBridge.isAvailable() && !forceInner) {
                _state.value = AriannaState(
                    error = "Termux not running",
                    isTermuxRequired = true,
                    query = query
                )
                return@launch
            }
            
            // Query Arianna
            val result = ariannaBridge.ask(
                query = query,
                useInner = forceInner
            )
            
            result.fold(
                onSuccess = { response ->
                    _state.value = AriannaState(
                        response = response,
                        isInner = forceInner,
                        timestamp = System.currentTimeMillis(),
                        query = query
                    )
                },
                onFailure = { error ->
                    _state.value = AriannaState(
                        error = error.message ?: "Unknown error",
                        isTermuxRequired = error.message?.contains("Termux") == true,
                        query = query
                    )
                }
            )
        }
    }
    
    /**
     * Clear current response
     */
    fun clear() {
        _state.value = AriannaState()
    }
    
    /**
     * Get conversation history
     */
    fun getHistory(): List<Pair<String, String>> {
        return ariannaBridge.getHistory()
    }
}

/**
 * UI State
 */
data class AriannaState(
    val query: String = "",
    val response: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isTermuxRequired: Boolean = false,
    val isInner: Boolean = false,
    val timestamp: Long = 0L
)

