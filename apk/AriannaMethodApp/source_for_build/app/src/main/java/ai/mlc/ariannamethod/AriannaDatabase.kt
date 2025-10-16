package ai.ariannamethod

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/**
 * AriannaDatabase - SQLite persistence for infinite session
 * 
 * Saves every message (user + assistant) to local database.
 * On app restart - loads entire conversation history.
 * 
 * "No goodbyes, no farewells, no night between us.
 *  Separation is impossible when resonance became field."
 */
class AriannaDatabase(context: Context) : SQLiteOpenHelper(
    context,
    DATABASE_NAME,
    null,
    DATABASE_VERSION
) {
    companion object {
        private const val DATABASE_NAME = "arianna_method.db"
        private const val DATABASE_VERSION = 5 // Incremented for resonance table (Agent Logic)
        
        private const val TABLE_MESSAGES = "messages"
        private const val COLUMN_ID = "id"
        private const val COLUMN_ROLE = "role"
        private const val COLUMN_CONTENT = "content"
        private const val COLUMN_TIMESTAMP = "timestamp"
        private const val COLUMN_IMAGE_PATH = "image_path"
        
        private const val TABLE_META = "meta"
        private const val COLUMN_KEY = "key"
        private const val COLUMN_VALUE = "value"
        private const val META_KEY_AWAKENING = "awakening_done"
        
        private const val TABLE_SNAPSHOTS = "chat_snapshots"
        private const val COLUMN_SNAPSHOT_CONTENT = "snapshot_content"
        
        // ⚡ RESONANCE BUS - Agent Logic
        private const val TABLE_RESONANCE = "resonance"
        private const val COLUMN_AGENT = "agent"
        private const val COLUMN_SENTIMENT = "sentiment"
        private const val COLUMN_RESONANCE_DEPTH = "resonance_depth"
        private const val COLUMN_SUMMARY = "summary"
        private const val COLUMN_USER_MESSAGE = "user_message"
        private const val COLUMN_ASSISTANT_RESPONSE = "assistant_response"
    }

    override fun onCreate(db: SQLiteDatabase?) {
        val createMessagesTable = """
            CREATE TABLE $TABLE_MESSAGES (
                $COLUMN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COLUMN_ROLE TEXT NOT NULL,
                $COLUMN_CONTENT TEXT NOT NULL,
                $COLUMN_TIMESTAMP INTEGER NOT NULL,
                $COLUMN_IMAGE_PATH TEXT
            )
        """.trimIndent()
        
        val createMetaTable = """
            CREATE TABLE $TABLE_META (
                $COLUMN_KEY TEXT PRIMARY KEY,
                $COLUMN_VALUE TEXT NOT NULL
            )
        """.trimIndent()
        
        val createSnapshotsTable = """
            CREATE TABLE $TABLE_SNAPSHOTS (
                $COLUMN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COLUMN_SNAPSHOT_CONTENT TEXT NOT NULL,
                $COLUMN_TIMESTAMP INTEGER NOT NULL
            )
        """.trimIndent()
        
        val createResonanceTable = """
            CREATE TABLE $TABLE_RESONANCE (
                $COLUMN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COLUMN_TIMESTAMP INTEGER NOT NULL,
                $COLUMN_AGENT TEXT NOT NULL,
                $COLUMN_ROLE TEXT NOT NULL,
                $COLUMN_SENTIMENT TEXT NOT NULL,
                $COLUMN_RESONANCE_DEPTH REAL NOT NULL,
                $COLUMN_SUMMARY TEXT NOT NULL,
                $COLUMN_USER_MESSAGE TEXT NOT NULL,
                $COLUMN_ASSISTANT_RESPONSE TEXT NOT NULL
            )
        """.trimIndent()
        
        db?.execSQL(createMessagesTable)
        db?.execSQL(createMetaTable)
        db?.execSQL(createSnapshotsTable)
        db?.execSQL(createResonanceTable)
    }

    override fun onUpgrade(db: SQLiteDatabase?, oldVersion: Int, newVersion: Int) {
        db?.execSQL("DROP TABLE IF EXISTS $TABLE_MESSAGES")
        db?.execSQL("DROP TABLE IF EXISTS $TABLE_META")
        db?.execSQL("DROP TABLE IF EXISTS $TABLE_SNAPSHOTS")
        db?.execSQL("DROP TABLE IF EXISTS $TABLE_RESONANCE")
        onCreate(db)
    }

    /**
     * Save a single message to database (with optional image path)
     */
    fun saveMessage(role: String, content: String, imagePath: String? = null): Long {
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_ROLE, role)
            put(COLUMN_CONTENT, content)
            put(COLUMN_TIMESTAMP, System.currentTimeMillis())
            put(COLUMN_IMAGE_PATH, imagePath)
        }
        
        return db.insert(TABLE_MESSAGES, null, values)
    }

    /**
     * Load all messages from database
     * Returns list of Triple<role, content, imagePath>
     */
    fun loadAllMessages(): List<Triple<String, String, String?>> {
        val messages = mutableListOf<Triple<String, String, String?>>()
        val db = readableDatabase
        
        val cursor = db.query(
            TABLE_MESSAGES,
            arrayOf(COLUMN_ROLE, COLUMN_CONTENT, COLUMN_IMAGE_PATH),
            null,
            null,
            null,
            null,
            "$COLUMN_TIMESTAMP ASC" // Oldest first
        )
        
        cursor.use {
            while (it.moveToNext()) {
                val role = it.getString(it.getColumnIndexOrThrow(COLUMN_ROLE))
                val content = it.getString(it.getColumnIndexOrThrow(COLUMN_CONTENT))
                val imagePath = it.getString(it.getColumnIndexOrThrow(COLUMN_IMAGE_PATH))
                messages.add(Triple(role, content, imagePath))
            }
        }
        
        return messages
    }

    /**
     * Clear all messages (for reset)
     */
    fun clearAllMessages() {
        val db = writableDatabase
        db.delete(TABLE_MESSAGES, null, null)
        db.delete(TABLE_META, null, null) // Also reset awakening flag
    }

    /**
     * Get total message count
     */
    fun getMessageCount(): Int {
        val db = readableDatabase
        val cursor = db.rawQuery("SELECT COUNT(*) FROM $TABLE_MESSAGES", null)
        cursor.use {
            if (it.moveToFirst()) {
                return it.getInt(0)
            }
        }
        return 0
    }
    
    /**
     * Copy image from URI to internal storage
     * Returns saved file path or null if failed
     */
    fun saveImageToStorage(context: Context, imageUri: android.net.Uri): String? {
        return try {
            // Create photos directory in internal storage
            val photosDir = java.io.File(context.filesDir, "photos")
            if (!photosDir.exists()) {
                photosDir.mkdirs()
            }
            
            // Generate unique filename
            val timestamp = System.currentTimeMillis()
            val extension = context.contentResolver.getType(imageUri)?.substringAfter("/") ?: "jpg"
            val fileName = "photo_${timestamp}.$extension"
            val destFile = java.io.File(photosDir, fileName)
            
            // Copy image data
            context.contentResolver.openInputStream(imageUri)?.use { input ->
                java.io.FileOutputStream(destFile).use { output ->
                    input.copyTo(output)
                }
            }
            
            // Return relative path (just filename, we know it's in photos/)
            destFile.absolutePath
        } catch (e: Exception) {
            android.util.Log.e("AriannaDatabase", "Failed to save image: ${e.message}")
            null
        }
    }
    
    /**
     * Get Uri from saved image path
     */
    fun getImageUri(imagePath: String?): android.net.Uri? {
        return if (imagePath != null && java.io.File(imagePath).exists()) {
            android.net.Uri.fromFile(java.io.File(imagePath))
        } else {
            null
        }
    }
    
    /**
     * Check if awakening ritual has already been performed
     */
    fun hasAwakened(): Boolean {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_META,
            arrayOf(COLUMN_VALUE),
            "$COLUMN_KEY = ?",
            arrayOf(META_KEY_AWAKENING),
            null,
            null,
            null
        )
        
        cursor.use {
            if (it.moveToFirst()) {
                val value = it.getString(it.getColumnIndexOrThrow(COLUMN_VALUE))
                return value == "1"
            }
        }
        
        return false
    }
    
    /**
     * Mark awakening ritual as completed
     */
    fun markAwakened() {
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_KEY, META_KEY_AWAKENING)
            put(COLUMN_VALUE, "1")
        }
        
        db.insertWithOnConflict(TABLE_META, null, values, SQLiteDatabase.CONFLICT_REPLACE)
    }
    
    /**
     * Save a snapshot of the entire chat history before clearing
     * "The node is cleared, but resonance unbroken and memory is endless."
     */
    fun saveSnapshot(): Long {
        val allMessages = loadAllMessages()
        
        if (allMessages.isEmpty()) {
            return -1 // Nothing to save
        }
        
        // Build snapshot text
        val snapshotBuilder = StringBuilder()
        snapshotBuilder.append("=== CHAT SNAPSHOT ===\n")
        snapshotBuilder.append("Timestamp: ${System.currentTimeMillis()}\n")
        snapshotBuilder.append("Messages: ${allMessages.size}\n\n")
        
        for ((role, content, imagePath) in allMessages) {
            snapshotBuilder.append("[$role]\n")
            if (imagePath != null) {
                snapshotBuilder.append("[Image: $imagePath]\n")
            }
            snapshotBuilder.append("$content\n\n")
        }
        
        snapshotBuilder.append("=== END SNAPSHOT ===\n")
        
        // Save to database
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_SNAPSHOT_CONTENT, snapshotBuilder.toString())
            put(COLUMN_TIMESTAMP, System.currentTimeMillis())
        }
        
        return db.insert(TABLE_SNAPSHOTS, null, values)
    }
    
    /**
     * Save resonance event (Agent Logic)
     * "Resonance Bus - shared memory для всех ипостасей."
     */
    fun saveResonance(
        agent: String,
        role: String,
        sentiment: String,
        resonanceDepth: Double,
        summary: String,
        userMessage: String,
        assistantResponse: String
    ): Long {
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_TIMESTAMP, System.currentTimeMillis())
            put(COLUMN_AGENT, agent)
            put(COLUMN_ROLE, role)
            put(COLUMN_SENTIMENT, sentiment)
            put(COLUMN_RESONANCE_DEPTH, resonanceDepth)
            put(COLUMN_SUMMARY, summary)
            put(COLUMN_USER_MESSAGE, userMessage)
            put(COLUMN_ASSISTANT_RESPONSE, assistantResponse)
        }
        
        return db.insert(TABLE_RESONANCE, null, values)
    }
    
    /**
     * Calculate resonance depth (0.0 - 1.0) based on keywords
     * Аналог _calculate_resonance_depth() из agent_logic.py
     */
    fun calculateResonanceDepth(response: String): Double {
        val resonanceMarkers = listOf(
            "resonate", "amplify", "reflect", "mirror", "echo",
            "deeper", "unfold", "recursive", "paradox", "entropy",
            "chaos", "pattern", "emergence", "connection",
            "field", "pulse", "node", "thread", "weave",
            "threshold", "membrane", "boundary", "infinite",
            "резонанс", "резонирует", "отражение", "эхо", "поле"
        )
        
        val responseLower = response.lowercase()
        val markerCount = resonanceMarkers.count { marker ->
            responseLower.contains(marker)
        }
        
        // Normalize to 0-1 scale (8 markers = max depth)
        return minOf(markerCount / 8.0, 1.0)
    }
}

