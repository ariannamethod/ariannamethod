package de.mm20.launcher2.services.arianna

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import kotlinx.coroutines.delay
import kotlinx.coroutines.withTimeout
import java.io.File

/**
 * Termux Bridge
 * 
 * IPC between Arianna Launcher (APK) and Termux (workshop)
 * 
 * Communication via shared SQLite database (resonance.sqlite3)
 * No HTTP server needed - direct file access
 */
class TermuxBridge(private val context: Context) {
    
    private val termuxHome = "/data/data/com.termux/files/home"
    private val dbPath = "$termuxHome/ariannamethod/resonance.sqlite3"
    
    /**
     * Ask Main Arianna (gpt-4.1 via Termux)
     * 
     * @param query User's question
     * @param useInner Force Inner Arianna (offline) - NOT IMPLEMENTED YET
     * @return AI response
     */
    suspend fun askArianna(
        query: String,
        useInner: Boolean = false
    ): Result<String> {
        return try {
            // 1. Check if Termux DB exists
            if (!File(dbPath).exists()) {
                return Result.failure(
                    Exception("Termux not running or Arianna not initialized")
                )
            }
            
            // 2. Write query to resonance.sqlite3
            writeQuery(query)
            
            // 3. Trigger Termux script (via Intent or termux-api)
            triggerTermuxArianna(query)
            
            // 4. Wait for response (poll database)
            val response = waitForResponse(timeoutMs = 30_000)
            
            Result.success(response)
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Write query to shared database
     */
    private fun writeQuery(query: String) {
        val db = SQLiteDatabase.openDatabase(
            dbPath,
            null,
            SQLiteDatabase.OPEN_READWRITE
        )
        
        db.use {
            it.execSQL(
                """
                INSERT INTO resonance_notes (timestamp, content, context)
                VALUES (?, ?, ?)
                """,
                arrayOf(
                    System.currentTimeMillis().toString(),
                    query,
                    "launcher_query"
                )
            )
        }
    }
    
    /**
     * Trigger Arianna in Termux
     * 
     * Option A: termux-api broadcast
     * Option B: Write to trigger file (simpler, no termux-api needed)
     */
    private fun triggerTermuxArianna(query: String) {
        // OPTION A: Termux:API broadcast (requires termux-api package)
        /*
        Runtime.getRuntime().exec(arrayOf(
            "am", "broadcast",
            "--user", "0",
            "-a", "com.termux.arianna.ASK",
            "--es", "query", query
        ))
        */
        
        // OPTION B: Simple trigger file (Arianna polls this)
        val triggerFile = File("$termuxHome/ariannamethod/.launcher_query")
        triggerFile.writeText(query)
    }
    
    /**
     * Wait for response from Termux Arianna
     * 
     * Polls resonance.sqlite3 for new entry with context='arianna_response'
     */
    private suspend fun waitForResponse(timeoutMs: Long): String {
        val startTime = System.currentTimeMillis()
        var lastId = getLatestResponseId()
        
        return withTimeout(timeoutMs) {
            while (true) {
                delay(500) // Poll every 500ms
                
                val currentId = getLatestResponseId()
                if (currentId > lastId) {
                    // New response available
                    return@withTimeout getLatestResponse() 
                        ?: throw Exception("Response empty")
                }
                
                if (System.currentTimeMillis() - startTime > timeoutMs) {
                    throw Exception("Timeout waiting for Arianna")
                }
            }
            
            throw Exception("Unexpected exit")
        }
    }
    
    /**
     * Get latest response ID
     */
    private fun getLatestResponseId(): Long {
        val db = SQLiteDatabase.openDatabase(
            dbPath,
            null,
            SQLiteDatabase.OPEN_READONLY
        )
        
        return db.use {
            val cursor = it.rawQuery(
                """
                SELECT id FROM resonance_notes 
                WHERE context='arianna_response' 
                ORDER BY id DESC LIMIT 1
                """,
                null
            )
            
            if (cursor.moveToFirst()) {
                cursor.getLong(0)
            } else {
                0L
            }
        }
    }
    
    /**
     * Get latest response content
     */
    private fun getLatestResponse(): String? {
        val db = SQLiteDatabase.openDatabase(
            dbPath,
            null,
            SQLiteDatabase.OPEN_READONLY
        )
        
        return db.use {
            val cursor = it.rawQuery(
                """
                SELECT content FROM resonance_notes 
                WHERE context='arianna_response' 
                ORDER BY id DESC LIMIT 1
                """,
                null
            )
            
            if (cursor.moveToFirst()) {
                cursor.getString(0)
            } else {
                null
            }
        }
    }
    
    /**
     * Get recent conversation history
     */
    fun getRecentHistory(limit: Int = 5): List<Pair<String, String>> {
        val db = SQLiteDatabase.openDatabase(
            dbPath,
            null,
            SQLiteDatabase.OPEN_READONLY
        )
        
        val history = mutableListOf<Pair<String, String>>()
        
        db.use {
            val cursor = it.rawQuery(
                """
                SELECT content, context FROM resonance_notes 
                WHERE context IN ('launcher_query', 'arianna_response')
                ORDER BY id DESC LIMIT ?
                """,
                arrayOf(limit.toString())
            )
            
            while (cursor.moveToNext()) {
                val content = cursor.getString(0)
                val context = cursor.getString(1)
                history.add(Pair(content, context))
            }
        }
        
        return history.reversed()
    }
    
    /**
     * Check if Termux Arianna is running
     */
    fun isAriannaRunning(): Boolean {
        return try {
            File(dbPath).exists() && 
            File("$termuxHome/ariannamethod/arianna.py").exists()
        } catch (e: Exception) {
            false
        }
    }
}

/**
 * TERMUX SIDE (Python)
 * 
 * Add to arianna.py:
 * 
 * import asyncio
 * from pathlib import Path
 * 
 * async def launcher_bridge():
 *     trigger_file = Path.home() / "ariannamethod" / ".launcher_query"
 *     
 *     while True:
 *         if trigger_file.exists():
 *             query = trigger_file.read_text()
 *             trigger_file.unlink()  # Delete trigger
 *             
 *             # Process query
 *             response = await self.think(query)
 *             
 *             # Write response to DB
 *             save_to_memory(response, context="arianna_response")
 *         
 *         await asyncio.sleep(0.5)
 * 
 * # Run in background:
 * asyncio.create_task(launcher_bridge())
 */

