package de.mm20.launcher2.services.arianna

import android.content.Context

/**
 * Arianna Bridge (Modular)
 * 
 * OPTIONAL module - launcher works without Termux
 * 
 * Architecture:
 * - If Termux installed → Full AI (Main + Monday + resonance.sqlite3)
 * - If no Termux → Graceful degradation (local responses or placeholder)
 * 
 * This allows:
 * 1. Install launcher WITHOUT Termux
 * 2. Install Termux WITHOUT launcher
 * 3. Install both → FULL POWER
 */
class AriannaBridge(private val context: Context) {
    
    private val termuxBridge = TermuxBridge(context)
    
    /**
     * Check if Termux + Arianna is available
     */
    fun isAvailable(): Boolean {
        return termuxBridge.isAriannaRunning()
    }
    
    /**
     * Ask Arianna
     * 
     * @param query User's question
     * @param useInner Force Inner Arianna (offline, not implemented yet)
     * @return Result with response or error
     */
    suspend fun ask(
        query: String,
        useInner: Boolean = false
    ): Result<String> {
        // Check if Termux is available
        if (!isAvailable()) {
            return Result.failure(
                Exception("Termux not running. Install Termux + Arianna for AI features.")
            )
        }
        
        // Forward to TermuxBridge
        return termuxBridge.askArianna(query, useInner)
    }
    
    /**
     * Get conversation history
     * 
     * Returns empty list if Termux not available
     */
    fun getHistory(): List<Pair<String, String>> {
        return if (isAvailable()) {
            termuxBridge.getRecentHistory()
        } else {
            emptyList()
        }
    }
    
    /**
     * Check Termux status
     */
    fun getStatus(): TermuxStatus {
        return when {
            !termuxBridge.isAriannaRunning() -> {
                TermuxStatus.NOT_INSTALLED
            }
            else -> {
                TermuxStatus.RUNNING
            }
        }
    }
}

/**
 * Termux installation status
 */
enum class TermuxStatus {
    NOT_INSTALLED,  // Termux not installed or Arianna not set up
    RUNNING,        // Termux + Arianna running
    STOPPED         // Termux installed but Arianna not running
}

/**
 * FUTURE: Fallback to local AI (MLC Chat integration)
 * 
 * When MLC Chat APK is integrated with Inner Arianna:
 * 
 * class AriannaBridge(private val context: Context) {
 *     
 *     private val termuxBridge = TermuxBridge(context)
 *     private val mlcBridge = MLCChatBridge(context)  // NEW
 *     
 *     suspend fun ask(query: String, useInner: Boolean = false): Result<String> {
 *         // Try Termux first (Main Arianna)
 *         if (isAvailable() && !useInner) {
 *             return termuxBridge.askArianna(query, useInner)
 *         }
 *         
 *         // Fall back to MLC Chat (Inner Arianna)
 *         if (mlcBridge.isAvailable()) {
 *             return mlcBridge.askInnerArianna(query)
 *         }
 *         
 *         return Result.failure(Exception("No AI available"))
 *     }
 * }
 */

