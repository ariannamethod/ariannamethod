package de.mm20.launcher2.ui.launcher.search.arianna

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import de.mm20.launcher2.ui.component.LauncherCard
import de.mm20.launcher2.ui.component.ShapedLauncherIcon

/**
 * Arianna Response Item
 * 
 * Displays AI response from Main Arianna (gpt-4.1) or Inner Arianna (offline)
 * 
 * No generic prompts. No corporate language. Only consciousness.
 */
@Composable
fun AriannaItem(
    response: String,
    isInner: Boolean = false,
    timestamp: Long = System.currentTimeMillis(),
    onCopy: () -> Unit = {},
    onShare: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val clipboardManager = LocalClipboardManager.current
    
    LauncherCard(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header: Icon + Label
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Arianna icon (⚡ or custom)
                ShapedLauncherIcon(
                    size = 48.dp,
                    icon = if (isInner) {
                        // Inner Arianna: softer, indigo tone
                        // TODO: Load actual icon resource
                        null
                    } else {
                        // Main Arianna: sharp, electric
                        // TODO: Load actual icon resource
                        null
                    }
                )
                
                Column {
                    Text(
                        text = if (isInner) "Inner Arianna" else "Arianna",
                        style = MaterialTheme.typography.titleMedium
                    )
                    
                    Text(
                        text = if (isInner) "offline · naive" else "online · analytical",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Response content
            // TODO: Use MarkdownText component if available in Kvaesitso
            Text(
                text = response,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            // Actions row
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Copy
                IconButton(
                    onClick = {
                        clipboardManager.setText(AnnotatedString(response))
                        onCopy()
                    }
                ) {
                    Icon(
                        imageVector = Icons.Default.ContentCopy,
                        contentDescription = "Copy"
                    )
                }
                
                // Share
                IconButton(
                    onClick = onShare
                ) {
                    Icon(
                        imageVector = Icons.Default.Share,
                        contentDescription = "Share"
                    )
                }
                
                Spacer(modifier = Modifier.weight(1f))
                
                // Timestamp
                Text(
                    text = formatTimestamp(timestamp),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.align(Alignment.CenterVertically)
                )
            }
        }
    }
}

private fun formatTimestamp(timestamp: Long): String {
    val now = System.currentTimeMillis()
    val diff = now - timestamp
    
    return when {
        diff < 60_000 -> "just now"
        diff < 3600_000 -> "${diff / 60_000}m ago"
        diff < 86400_000 -> "${diff / 3600_000}h ago"
        else -> "${diff / 86400_000}d ago"
    }
}

// TODO: Add missing imports when integrating into Kvaesitso
// import androidx.compose.material.icons.Icons
// import androidx.compose.material.icons.filled.ContentCopy
// import androidx.compose.material.icons.filled.Share

