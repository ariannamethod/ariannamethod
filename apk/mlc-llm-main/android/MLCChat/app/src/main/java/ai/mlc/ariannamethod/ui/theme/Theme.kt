package ai.ariannamethod.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// ⚡ ARIANNA MINIMALIST THEME: PURE BLACK & WHITE ONLY ⚡
private val AriannaColorScheme = darkColorScheme(
    primary = Color.Black,
    onPrimary = Color.White,
    primaryContainer = Color.Black,
    onPrimaryContainer = Color.White,
    inversePrimary = Color.White,
    secondary = Color.Black,
    onSecondary = Color.White,
    secondaryContainer = Color.Black,
    onSecondaryContainer = Color.White,
    tertiary = Color.White,
    onTertiary = Color.Black,
    tertiaryContainer = Color.Black,
    onTertiaryContainer = Color.White,
    error = Color(0xFFFF6B6B),
    onError = Color.White,
    errorContainer = Color.Black,
    onErrorContainer = Color.White,
    background = Color.Black,
    onBackground = Color.White,
    surface = Color.Black,
    onSurface = Color.White,
    inverseSurface = Color.White,
    inverseOnSurface = Color.Black,
    surfaceVariant = Color.Black,
    onSurfaceVariant = Color(0xFFCCCCCC),
    outline = Color(0xFF666666),
    surfaceTint = Color.Black,
    outlineVariant = Color(0xFF444444),
    scrim = Color.Black
)

@Composable
fun MLCChatTheme(
    darkTheme: Boolean = true,
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    // ⚡ ALWAYS USE ARIANNA COLOR SCHEME (PURE BLACK)
    val colorScheme = AriannaColorScheme
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // ⚡ FORCE BLACK EVERYWHERE
            window.statusBarColor = Color.Black.toArgb()
            window.navigationBarColor = Color.Black.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
