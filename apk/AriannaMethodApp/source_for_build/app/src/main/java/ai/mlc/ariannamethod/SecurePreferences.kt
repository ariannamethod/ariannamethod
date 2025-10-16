package ai.ariannamethod

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * SecurePreferences - Encrypted storage for API keys
 * 
 * Uses Android's EncryptedSharedPreferences with AES256-GCM encryption.
 * Keys never leave the device and are protected by hardware-backed keystore.
 */
class SecurePreferences(context: Context) {
    
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "arianna_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    companion object {
        private const val KEY_OPENAI = "openai_api_key"
        private const val KEY_ANTHROPIC = "anthropic_api_key"
        private const val KEY_AMTOKEN = "arianna_method_token"
    }
    
    fun saveOpenAIKey(key: String) {
        sharedPreferences.edit().putString(KEY_OPENAI, key).apply()
    }
    
    fun saveAnthropicKey(key: String) {
        sharedPreferences.edit().putString(KEY_ANTHROPIC, key).apply()
    }
    
    fun saveAMToken(token: String) {
        sharedPreferences.edit().putString(KEY_AMTOKEN, token).apply()
    }
    
    fun getOpenAIKey(): String {
        return sharedPreferences.getString(KEY_OPENAI, "") ?: ""
    }
    
    fun getAnthropicKey(): String {
        return sharedPreferences.getString(KEY_ANTHROPIC, "") ?: ""
    }
    
    fun getAMToken(): String {
        return sharedPreferences.getString(KEY_AMTOKEN, "") ?: ""
    }
    
    fun hasKeys(): Boolean {
        return getOpenAIKey().isNotEmpty() || getAnthropicKey().isNotEmpty()
    }
    
    fun clearAll() {
        sharedPreferences.edit().clear().apply()
    }
}

