package ai.ariannamethod

import android.app.Activity
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@ExperimentalMaterial3Api
@Composable
fun NavView(activity: Activity, appViewModel: AppViewModel = viewModel()) {
    val navController = rememberNavController()
    val securePrefs = SecurePreferences(activity.applicationContext)
    
    // BETA: Start directly in chat - no model selection screen
    NavHost(navController = navController, startDestination = "chat") {
        // composable("home") { StartView(navController, appViewModel) } // REMOVED: Skip model selection
        composable("chat") { ChatView(navController, appViewModel.chatState, activity) }
        composable("settings") {
            SettingsView(
                navController = navController,
                onSave = { openaiKey, anthropicKey, amToken ->
                    securePrefs.saveOpenAIKey(openaiKey)
                    securePrefs.saveAnthropicKey(anthropicKey)
                    securePrefs.saveAMToken(amToken)
                    // Update API client with new keys
                    AriannaAPIClient.openaiApiKey = openaiKey
                    AriannaAPIClient.anthropicApiKey = anthropicKey
                    AriannaAPIClient.amToken = amToken
                },
                currentOpenAIKey = securePrefs.getOpenAIKey(),
                currentAnthropicKey = securePrefs.getAnthropicKey(),
                currentAMToken = securePrefs.getAMToken()
            )
        }
    }
}
