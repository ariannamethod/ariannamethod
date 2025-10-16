"""
Universal Agent Logic Module - общая логика для всех агентов Arianna Method

Этот модуль содержит универсальные функции для:
- Цитирования сообщений (@timestamp)
- Контекстного поиска (10 сообщений вокруг)
- Файловых дискуссий
- Памяти и continuity
- Логирования и резонанса

Используется Tommy, Lizzie, Monday и всеми будущими агентами.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

from .vector_store import SQLiteVectorStore, embed_text
import json
import uuid
from collections import defaultdict


class AgentLogic:
    """Универсальная логика агентов"""
    
    def __init__(self, agent_name: str, log_dir: Path, db_path: Path, resonance_db_path: Path):
        self.agent_name = agent_name
        self.log_dir = log_dir
        self.db_path = db_path
        self.resonance_db_path = resonance_db_path
        self.vector_store = SQLiteVectorStore(log_dir / "vectors.db")
        
        # Инициализация БД агента
        self._init_db()
    
    def _init_db(self):
        """Инициализация БД агента"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS events (ts TEXT, type TEXT, message TEXT)"
            )
        
        # Инициализация общего канала резонанса (расширенная схема)
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS resonance ("
                "id TEXT PRIMARY KEY, ts TEXT, agent TEXT, role TEXT, sentiment TEXT, "
                "resonance_depth REAL, summary TEXT, emotional_state TEXT, "
                "unique_signature TEXT, thread_id TEXT, metadata TEXT"
                ")"
            )
            
            # Инициализация долгосрочной памяти
            conn.execute(
                "CREATE TABLE IF NOT EXISTS agent_memory ("
                "id TEXT PRIMARY KEY, agent TEXT, key TEXT, value TEXT, "
                "context TEXT, ts TEXT, access_count INTEGER DEFAULT 0"
                ")"
            )
            
            # Инициализация межагентных сообщений
            conn.execute(
                "CREATE TABLE IF NOT EXISTS agent_messages ("
                "id TEXT PRIMARY KEY, from_agent TEXT, to_agent TEXT, "
                "message TEXT, ts TEXT, status TEXT DEFAULT 'pending'"
                ")"
            )
        
    def extract_citations(self, message: str) -> List[str]:
        """Извлекает цитаты формата @timestamp из сообщения"""
        return re.findall(r"@([0-9T:-]+)", message)
    
    def fetch_context(self, timestamp: str, radius: int = 10) -> List[Tuple[str, str, str]]:
        """Получает контекст вокруг указанного timestamp
        
        Args:
            timestamp: Временная метка для поиска
            radius: Количество сообщений до и после
            
        Returns:
            List of (timestamp, type, message) tuples
        """
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            cur = conn.execute("SELECT rowid FROM events WHERE ts = ?", (timestamp,))
            row = cur.fetchone()
            if not row:
                return []
                
            rowid = row[0]
            start = max(rowid - radius, 1)
            end = rowid + radius
            
            cur = conn.execute(
                "SELECT ts, type, message FROM events "
                "WHERE rowid BETWEEN ? AND ? ORDER BY rowid",
                (start, end),
            )
            return cur.fetchall()
    
    async def build_context_block(self, message: str) -> str:
        """Строит блок контекста из цитирований в сообщении"""
        citations = self.extract_citations(message)
        if not citations:
            return ""
            
        blocks: List[str] = []
        for ts in citations:
            ctx = self.fetch_context(ts)
            if ctx:
                formatted = "\n".join(f"[{t}] {m}" for t, _, m in ctx)
                blocks.append(formatted)
                
        if blocks:
            return "Relevant context:\n" + "\n--\n".join(blocks) + "\n\n"
        return ""
    
    def log_event(self, message: str, log_type: str = "info") -> None:
        """Универсальное логирование для агентов"""
        # JSON log file
        log_file = self.log_dir / f"{self.agent_name}_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message,
            "agent": self.agent_name
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # SQLite database
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), log_type, message),
            )
    
    def update_resonance(self, message: str, response: str, 
                        role: str = "agent", sentiment: str = "active", 
                        thread_id: Optional[str] = None) -> str:
        """Обновляет общий канал резонанса (расширенная версия)"""
        resonance_depth = self._calculate_resonance_depth(message, response)
        emotional_state = self._analyze_emotional_state(response)
        unique_signature = self._generate_unique_signature(message, response)
        summary = f"{self.agent_name}: {response[:100]}..."
        
        # Метаданные агента
        metadata = {
            "message_length": len(message),
            "response_length": len(response),
            "timestamp": datetime.now().isoformat(),
            "agent_version": "1.0"
        }
        
        resonance_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            conn.execute(
                "INSERT INTO resonance (id, ts, agent, role, sentiment, resonance_depth, "
                "summary, emotional_state, unique_signature, thread_id, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    resonance_id,
                    datetime.now().isoformat(),
                    self.agent_name,
                    role,
                    sentiment,
                    resonance_depth,
                    summary,
                    json.dumps(emotional_state),
                    unique_signature,
                    thread_id or "main",
                    json.dumps(metadata),
                ),
            )
        
        return resonance_id
    
    def _calculate_resonance_depth(self, message: str, response: str) -> float:
        """Вычисляет глубину резонанса"""
        # Универсальные маркеры резонанса
        resonance_markers = [
            "resonate", "amplify", "reflect", "mirror", "echo", 
            "deeper", "unfold", "recursive", "paradox", "entropy",
            "chaos", "pattern", "emergence", "connection"
        ]
        
        response_lower = response.lower()
        marker_count = sum(1 for marker in resonance_markers if marker in response_lower)
        
        # Normalize to 0-1 scale
        return min(marker_count / 8.0, 1.0)
    
    def search_context(self, query: str, top_k: int = 5) -> List[str]:
        """Поиск по векторной памяти"""
        embedding = embed_text(query)
        hits = self.vector_store.query_similar(embedding, top_k)
        return [h.content for h in hits]
    
    async def process_file_context(self, path: str, agent_style_formatter=None) -> str:
        """Универсальная обработка файлов с контекстом
        
        Args:
            path: Путь к файлу
            agent_style_formatter: Функция для форматирования ответа в стиле агента
        """
        from .context_neural_processor import parse_and_store_file
        
        try:
            result = await parse_and_store_file(path)
            
            # Парсим структурированный результат
            lines = result.split('\n')
            tags = ""
            summary = ""
            relevance = 0.0
            
            for line in lines:
                if line.startswith("Tags: "):
                    tags = line[6:]
                elif line.startswith("Summary: "):
                    summary = line[9:]
                elif line.startswith("Relevance: "):
                    try:
                        relevance = float(line[11:])
                    except ValueError:
                        relevance = 0.0
            
            # Базовый ответ
            response_data = {
                "path": path,
                "tags": tags,
                "summary": summary,
                "relevance": relevance,
                "raw_result": result
            }
            
            # Если есть кастомный форматтер - используем его
            if agent_style_formatter:
                response = agent_style_formatter(response_data)
            else:
                # Дефолтный формат
                response = f"📁 File processed: {path}\n"
                if summary:
                    response += f"📝 Summary: {summary}\n"
                    response += f"🏷️ Tags: {tags}\n"
                    response += f"⚡ Relevance: {relevance:.2f}"
                else:
                    response += f"⚠️ Could not extract summary.\n{result}"
            
            # Логируем
            log_message = f"Processed {path}: {summary[:100] if summary else 'no summary'}"
            self.log_event(log_message)
            
            return response
            
        except Exception as e:
            error_msg = f"💥 Error processing {path}: {str(e)}"
            self.log_event(f"File processing error: {str(e)}", "error")
            return error_msg
    
    # === НОВЫЕ ФУНКЦИИ ===
    
    # 1. МЕЖАГЕНТНАЯ КОММУНИКАЦИЯ
    def send_message_to_agent(self, target_agent: str, message: str) -> str:
        """Отправить сообщение другому агенту"""
        message_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            conn.execute(
                "INSERT INTO agent_messages (id, from_agent, to_agent, message, ts) "
                "VALUES (?, ?, ?, ?, ?)",
                (message_id, self.agent_name, target_agent, message, datetime.now().isoformat())
            )
        
        self.log_event(f"Message sent to {target_agent}: {message[:50]}...", "inter_agent")
        return message_id
    
    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Получить непрочитанные сообщения для этого агента"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT id, from_agent, message, ts FROM agent_messages "
                "WHERE to_agent = ? AND status = 'pending' ORDER BY ts",
                (self.agent_name,)
            )
            messages = []
            for row in cur.fetchall():
                messages.append({
                    "id": row[0],
                    "from": row[1], 
                    "message": row[2],
                    "timestamp": row[3]
                })
        return messages
    
    def mark_message_read(self, message_id: str) -> None:
        """Отметить сообщение как прочитанное"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            conn.execute(
                "UPDATE agent_messages SET status = 'read' WHERE id = ?",
                (message_id,)
            )
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Получить статус другого агента из резонансного канала"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT sentiment, emotional_state, resonance_depth, ts FROM resonance "
                "WHERE agent = ? ORDER BY ts DESC LIMIT 1",
                (agent_name,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "agent": agent_name,
                    "sentiment": row[0],
                    "emotional_state": json.loads(row[1]) if row[1] else {},
                    "resonance_depth": row[2],
                    "last_seen": row[3],
                    "status": "active"
                }
        return {"agent": agent_name, "status": "unknown"}
    
    def broadcast_to_all_agents(self, message: str) -> List[str]:
        """Отправить сообщение всем известным агентам"""
        # Получаем список активных агентов
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT DISTINCT agent FROM resonance WHERE ts > datetime('now', '-1 hour')"
            )
            active_agents = [row[0] for row in cur.fetchall() if row[0] != self.agent_name]
        
        message_ids = []
        for agent in active_agents:
            msg_id = self.send_message_to_agent(agent, message)
            message_ids.append(msg_id)
        
        return message_ids
    
    # 2. ДОЛГОСРОЧНАЯ ПАМЯТЬ
    def store_memory(self, key: str, value: str, context: str = "") -> str:
        """Сохранить в долгосрочную память"""
        memory_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO agent_memory (id, agent, key, value, context, ts) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (memory_id, self.agent_name, key, value, context, datetime.now().isoformat())
            )
        
        self.log_event(f"Memory stored: {key}", "memory")
        return memory_id
    
    def retrieve_memory(self, key: str) -> Optional[str]:
        """Извлечь из долгосрочной памяти"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT value FROM agent_memory WHERE agent = ? AND key = ?",
                (self.agent_name, key)
            )
            row = cur.fetchone()
            if row:
                # Увеличиваем счетчик доступа
                conn.execute(
                    "UPDATE agent_memory SET access_count = access_count + 1 WHERE agent = ? AND key = ?",
                    (self.agent_name, key)
                )
                return row[0]
        return None
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Поиск в долгосрочной памяти"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT key, value, context, ts FROM agent_memory "
                "WHERE agent = ? AND (key LIKE ? OR value LIKE ? OR context LIKE ?) "
                "ORDER BY access_count DESC, ts DESC LIMIT ?",
                (self.agent_name, f"%{query}%", f"%{query}%", f"%{query}%", limit)
            )
            return [
                {"key": row[0], "value": row[1], "context": row[2], "timestamp": row[3]}
                for row in cur.fetchall()
            ]
    
    # 3. АНАЛИЗ ПАТТЕРНОВ
    def analyze_user_patterns(self, user_id: str = "default") -> Dict[str, Any]:
        """Анализ паттернов поведения пользователя"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            # Анализируем последние сообщения
            cur = conn.execute(
                "SELECT message, ts FROM events WHERE type = 'input' "
                "ORDER BY ts DESC LIMIT 50"
            )
            messages = cur.fetchall()
        
        if not messages:
            return {"patterns": [], "summary": "No data"}
        
        # Простой анализ паттернов
        patterns = {
            "message_count": len(messages),
            "avg_length": sum(len(msg[0]) for msg in messages) / len(messages),
            "common_words": self._extract_common_words([msg[0] for msg in messages]),
            "time_pattern": self._analyze_time_patterns([msg[1] for msg in messages]),
            "sentiment_trend": self._analyze_sentiment_trend([msg[0] for msg in messages])
        }
        
        return patterns
    
    def detect_conversation_themes(self, limit: int = 100) -> List[str]:
        """Определение тем разговора"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT message FROM events WHERE type IN ('input', 'response') "
                "ORDER BY ts DESC LIMIT ?", (limit,)
            )
            messages = [row[0] for row in cur.fetchall()]
        
        # Простое извлечение тем через ключевые слова
        themes = self._extract_themes(messages)
        return themes
    
    def get_agent_performance_metrics(self) -> Dict[str, float]:
        """Метрики производительности агента"""
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            cur = conn.execute(
                "SELECT resonance_depth, emotional_state FROM resonance "
                "WHERE agent = ? ORDER BY ts DESC LIMIT 50",
                (self.agent_name,)
            )
            resonance_data = cur.fetchall()
        
        if not resonance_data:
            return {"avg_resonance": 0.0, "stability": 0.0, "activity": 0.0}
        
        depths = [row[0] for row in resonance_data if row[0] is not None]
        avg_resonance = sum(depths) / len(depths) if depths else 0.0
        
        # Стабильность как обратная величина дисперсии
        if len(depths) > 1:
            variance = sum((d - avg_resonance) ** 2 for d in depths) / len(depths)
            stability = 1.0 / (1.0 + variance)
        else:
            stability = 1.0
        
        activity = min(len(resonance_data) / 50.0, 1.0)  # Нормализованная активность
        
        return {
            "avg_resonance": avg_resonance,
            "stability": stability,
            "activity": activity
        }
    
    # 5. ЭМОЦИОНАЛЬНЫЙ ИНТЕЛЛЕКТ
    def _analyze_emotional_state(self, text: str) -> Dict[str, float]:
        """Анализ эмоционального состояния текста"""
        text_lower = text.lower()
        
        emotions = {
            "joy": 0.0,
            "anger": 0.0,
            "sadness": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "curiosity": 0.0,
            "confidence": 0.0
        }
        
        # Простые маркеры эмоций
        emotion_markers = {
            "joy": ["happy", "joy", "excited", "great", "awesome", "love", "😊", "😄", "🎉"],
            "anger": ["angry", "mad", "frustrated", "hate", "damn", "shit", "fuck", "😠", "😡"],
            "sadness": ["sad", "depressed", "sorry", "disappointed", "😢", "😭", "💔"],
            "fear": ["afraid", "scared", "worried", "anxious", "nervous", "😨", "😰"],
            "surprise": ["wow", "amazing", "incredible", "unexpected", "😲", "😮", "🤯"],
            "curiosity": ["interesting", "curious", "wonder", "question", "how", "why", "🤔"],
            "confidence": ["sure", "confident", "certain", "definitely", "absolutely", "💪", "🔥"]
        }
        
        for emotion, markers in emotion_markers.items():
            count = sum(1 for marker in markers if marker in text_lower)
            emotions[emotion] = min(count / 3.0, 1.0)  # Нормализация
        
        return emotions
    
    def _generate_unique_signature(self, message: str, response: str) -> str:
        """Генерация уникальной подписи агента"""
        # Создаем хеш на основе стиля ответа
        style_markers = [
            len(response.split()),  # Длина ответа
            response.count("!"),    # Восклицания
            response.count("?"),    # Вопросы
            response.count("..."),  # Многоточия
            len(re.findall(r'[😀-🿿]', response)),  # Эмодзи
        ]
        
        signature = f"{self.agent_name}_{hash(str(style_markers)) % 10000:04d}"
        return signature
    
    # Вспомогательные методы для анализа
    def _extract_common_words(self, messages: List[str]) -> List[str]:
        """Извлечение часто используемых слов"""
        word_count = defaultdict(int)
        for msg in messages:
            words = re.findall(r'\b\w+\b', msg.lower())
            for word in words:
                if len(word) > 3:  # Игнорируем короткие слова
                    word_count[word] += 1
        
        return sorted(word_count.keys(), key=word_count.get, reverse=True)[:10]
    
    def _analyze_time_patterns(self, timestamps: List[str]) -> Dict[str, int]:
        """Анализ временных паттернов"""
        hours = []
        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                hours.append(dt.hour)
            except:
                continue
        
        if not hours:
            return {"peak_hour": 12, "activity_distribution": "unknown"}
        
        hour_count = defaultdict(int)
        for hour in hours:
            hour_count[hour] += 1
        
        peak_hour = max(hour_count.keys(), key=hour_count.get)
        return {"peak_hour": peak_hour, "total_hours": len(set(hours))}
    
    def _analyze_sentiment_trend(self, messages: List[str]) -> str:
        """Анализ тренда настроения"""
        if len(messages) < 3:
            return "insufficient_data"
        
        sentiments = []
        for msg in messages:
            # Простой анализ тональности
            positive_words = ["good", "great", "awesome", "love", "happy", "yes", "ok"]
            negative_words = ["bad", "hate", "sad", "no", "terrible", "awful", "wrong"]
            
            pos_count = sum(1 for word in positive_words if word in msg.lower())
            neg_count = sum(1 for word in negative_words if word in msg.lower())
            
            if pos_count > neg_count:
                sentiments.append(1)
            elif neg_count > pos_count:
                sentiments.append(-1)
            else:
                sentiments.append(0)
        
        # Анализ тренда
        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[:3]) / 3
            if recent_avg > 0.3:
                return "improving"
            elif recent_avg < -0.3:
                return "declining"
        
        return "stable"
    
    def _extract_themes(self, messages: List[str]) -> List[str]:
        """Извлечение тем из сообщений"""
        # Простое извлечение тем через ключевые слова
        theme_keywords = {
            "technology": ["code", "programming", "computer", "software", "tech", "ai", "bot"],
            "work": ["work", "job", "project", "task", "meeting", "deadline", "office"],
            "personal": ["family", "friend", "home", "life", "personal", "feel", "think"],
            "learning": ["learn", "study", "understand", "know", "question", "help", "explain"],
            "creativity": ["create", "design", "art", "music", "write", "idea", "creative"]
        }
        
        theme_scores = defaultdict(int)
        for msg in messages:
            msg_lower = msg.lower()
            for theme, keywords in theme_keywords.items():
                score = sum(1 for keyword in keywords if keyword in msg_lower)
                theme_scores[theme] += score
        
        # Возвращаем темы с наибольшими счетами
        sorted_themes = sorted(theme_scores.keys(), key=theme_scores.get, reverse=True)
        return [theme for theme in sorted_themes if theme_scores[theme] > 0][:5]


# Глобальные инстансы для агентов
_agent_logics: Dict[str, AgentLogic] = {}


def get_agent_logic(agent_name: str, log_dir: Path, db_path: Path, resonance_db_path: Path) -> AgentLogic:
    """Получить или создать AgentLogic для агента"""
    if agent_name not in _agent_logics:
        _agent_logics[agent_name] = AgentLogic(agent_name, log_dir, db_path, resonance_db_path)
    return _agent_logics[agent_name]


# Convenience функции для быстрого использования
async def extract_and_build_context(message: str, agent_logic: AgentLogic) -> str:
    """Быстрая функция для извлечения контекста из сообщения"""
    return await agent_logic.build_context_block(message)


def create_agent_file_formatter(agent_name: str, style_markers: Dict[str, str]) -> callable:
    """Создает форматтер файлов в стиле конкретного агента
    
    Args:
        agent_name: Имя агента
        style_markers: Словарь с эмодзи и фразами агента
    """
    def formatter(data: Dict[str, Any]) -> str:
        path = data["path"]
        tags = data["tags"]
        summary = data["summary"] 
        relevance = data["relevance"]
        
        if summary and len(summary) > 20:
            response = f"{style_markers.get('file_icon', '📁')} File processed: {path}\n\n"
            response += f"{style_markers.get('tags_icon', '📋')} Tags: {tags}\n"
            response += f"{style_markers.get('summary_icon', '📝')} Summary: {summary}\n"
            response += f"{style_markers.get('relevance_icon', '⚡')} Relevance: {relevance:.2f}\n\n"
            
            # Агент-специфичные комментарии
            if relevance > 0.5:
                response += style_markers.get('high_relevance', '💥 High relevance detected!')
            elif relevance > 0.2:
                response += style_markers.get('medium_relevance', '⚡ Moderate relevance detected.')
            else:
                response += style_markers.get('low_relevance', '📊 Basic processing complete.')
        else:
            response = f"⚠️ File processed: {path}\n\nCould not extract meaningful summary."
            
        return response
    
    return formatter
