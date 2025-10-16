package de.mm20.launcher2.ui.launcher.search.arianna

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

/**
 * Arianna Results Section
 * 
 * Displays AI responses in search results
 * Optional module - works without Termux
 */
@Composable
fun AriannaResults(
    searchQuery: String,
    modifier: Modifier = Modifier,
    viewModel: AriannaVM = viewModel()
) {
    // Only show if query looks like AI question
    if (!shouldShowArianna(searchQuery)) {
        return
    }
    
    val state by viewModel.state.collectAsState()
    
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Section header
        Text(
            text = if (state.isInner) "Inner Arianna" else "Arianna",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )
        
        when {
            // Loading
            state.isLoading -> {
                AriannaLoadingItem()
            }
            
            // Error (e.g. Termux not running)
            state.error != null -> {
                AriannaErrorItem(
                    error = state.error,
                    isTermuxRequired = state.isTermuxRequired,
                    onRetry = { viewModel.askArianna(searchQuery) }
                )
            }
            
            // Success - show response
            state.response != null -> {
                AriannaItem(
                    response = state.response!!,
                    isInner = state.isInner,
                    timestamp = state.timestamp,
                    onCopy = { /* TODO: implement */ },
                    onShare = { /* TODO: implement */ }
                )
            }
        }
    }
    
    // Trigger query when search changes
    LaunchedEffect(searchQuery) {
        if (shouldShowArianna(searchQuery)) {
            viewModel.askArianna(searchQuery)
        }
    }
}

/**
 * Loading indicator
 */
@Composable
private fun AriannaLoadingItem() {
    LauncherCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp)
            )
            Text(
                text = "Thinking...",
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

/**
 * Error state
 */
@Composable
private fun AriannaErrorItem(
    error: String,
    isTermuxRequired: Boolean,
    onRetry: () -> Unit
) {
    LauncherCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = if (isTermuxRequired) {
                    "⚡ Termux not running"
                } else {
                    "⚠️ $error"
                },
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.error
            )
            
            if (isTermuxRequired) {
                Text(
                    text = "Install Termux + Arianna for full AI capabilities",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // TODO: Add link to installation guide
            } else {
                TextButton(onClick = onRetry) {
                    Text("Retry")
                }
            }
        }
    }
}

/**
 * Determine if query should trigger Arianna
 */
private fun shouldShowArianna(query: String): Boolean {
    if (query.length < 3) return false
    
    // Trigger on questions
    val questionWords = listOf("what", "why", "how", "when", "where", "who", "which")
    val lowerQuery = query.lowercase()
    
    if (questionWords.any { lowerQuery.startsWith(it) }) {
        return true
    }
    
    // Trigger on explicit "@arianna"
    if (lowerQuery.startsWith("@arianna") || lowerQuery.startsWith("@inner")) {
        return true
    }
    
    // Trigger on question mark
    if (query.contains("?")) {
        return true
    }
    
    return false
}

// TODO: Add import when integrating
// import de.mm20.launcher2.ui.component.LauncherCard

