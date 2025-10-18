#!/usr/bin/env python3
"""
Field Memory - Модуль долговременной памяти без весов
Хранит и извлекает контекстную информацию для поддержания связности разговоров.
Использует семантический поиск и ассоциативные связи.
"""

import sqlite3
import json
import time
import math
import threading
import sys
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, deque
import h2o

@dataclass
class MemoryEntry:
    """Запись в памяти"""
    id: str
    content: str
    context: str
    timestamp: float
    importance: float
    access_count: int = 0
    last_access: float = 0.0
    associations: List[str] = None
    
    def __post_init__(self):
        if self.associations is None:
            self.associations = []

class SemanticIndex:
    """Семантический индекс для быстрого поиска без векторных баз"""
    
    def __init__(self):
        self.word_to_entries = defaultdict(set)
        self.bigram_to_entries = defaultdict(set)
        self.trigram_to_entries = defaultdict(set)
        
    def index_entry(self, entry: MemoryEntry):
        """Индексирует запись для поиска"""
        words = self._extract_words(entry.content + " " + entry.context)
        
        # Индексируем по словам
        for word in words:
            self.word_to_entries[word].add(entry.id)
            
        # Индексируем по биграммам
        for i in range(len(words) - 1):
            bigram = (words[i], words[i + 1])
            self.bigram_to_entries[bigram].add(entry.id)
            
        # Индексируем по триграммам
        for i in range(len(words) - 2):
            trigram = (words[i], words[i + 1], words[i + 2])
            self.trigram_to_entries[trigram].add(entry.id)
            
    def search(self, query: str, limit: int = 10) -> Set[str]:
        """Поиск по запросу, возвращает ID записей"""
        query_words = self._extract_words(query)
        
        if not query_words:
            return set()
            
        # Поиск по словам
        word_matches = set()
        for word in query_words:
            word_matches.update(self.word_to_entries.get(word, set()))
            
        # Поиск по биграммам
        bigram_matches = set()
        for i in range(len(query_words) - 1):
            bigram = (query_words[i], query_words[i + 1])
            bigram_matches.update(self.bigram_to_entries.get(bigram, set()))
            
        # Поиск по триграммам (наивысший приоритет)
        trigram_matches = set()
        for i in range(len(query_words) - 2):
            trigram = (query_words[i], query_words[i + 1], query_words[i + 2])
            trigram_matches.update(self.trigram_to_entries.get(trigram, set()))
            
        # Объединяем результаты с весами
        all_matches = []
        
        for entry_id in trigram_matches:
            all_matches.append((entry_id, 3.0))  # Триграммы весят больше
            
        for entry_id in bigram_matches:
            if entry_id not in trigram_matches:
                all_matches.append((entry_id, 2.0))  # Биграммы средний вес
                
        for entry_id in word_matches:
            if entry_id not in trigram_matches and entry_id not in bigram_matches:
                all_matches.append((entry_id, 1.0))  # Слова минимальный вес
                
        # Сортируем по релевантности и ограничиваем
        all_matches.sort(key=lambda x: x[1], reverse=True)
        return {match[0] for match in all_matches[:limit]}
        
    def _extract_words(self, text: str) -> List[str]:
        """Извлекает слова из текста"""
        # Простая токенизация
        words = text.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        return [word for word in words if len(word) > 2]  # Фильтруем короткие слова

class AssociativeNetwork:
    """Ассоциативная сеть для связывания концепций"""
    
    def __init__(self):
        self.associations = defaultdict(lambda: defaultdict(float))
        self.concept_strength = defaultdict(float)
        
    def add_association(self, concept1: str, concept2: str, strength: float = 1.0):
        """Добавляет ассоциацию между концепциями"""
        self.associations[concept1][concept2] += strength
        self.associations[concept2][concept1] += strength
        self.concept_strength[concept1] += strength * 0.5
        self.concept_strength[concept2] += strength * 0.5
        
    def get_related_concepts(self, concept: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Возвращает связанные концепции"""
        if concept not in self.associations:
            return []
            
        related = list(self.associations[concept].items())
        related.sort(key=lambda x: x[1], reverse=True)
        return related[:limit]
        
    def strengthen_association(self, concept1: str, concept2: str, factor: float = 1.1):
        """Усиливает ассоциацию между концепциями"""
        if concept2 in self.associations[concept1]:
            self.associations[concept1][concept2] *= factor
            self.associations[concept2][concept1] *= factor
            
    def decay_associations(self, decay_factor: float = 0.99):
        """Ослабляет все ассоциации (забывание)"""
        for concept1 in self.associations:
            for concept2 in list(self.associations[concept1].keys()):
                self.associations[concept1][concept2] *= decay_factor
                if self.associations[concept1][concept2] < 0.01:
                    del self.associations[concept1][concept2]

class FieldMemoryCore:
    """Ядро системы памяти Field"""
    
    def __init__(self, db_path: str = "field_memory.db"):
        self.db_path = db_path
        self.semantic_index = SemanticIndex()
        self.associative_network = AssociativeNetwork()
        self.memory_cache = {}
        self.recent_memories = deque(maxlen=100)
        self.memory_lock = threading.Lock()
        self.init_database()
        self.load_memories_to_cache()
        
    def init_database(self):
        """Инициализация базы памяти"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Новые таблицы для продвинутой памяти
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_entries (
            id TEXT PRIMARY KEY,
            content TEXT,
            context TEXT,
            timestamp REAL,
            importance REAL,
            access_count INTEGER DEFAULT 0,
            last_access REAL DEFAULT 0,
            associations TEXT,
            metadata TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS concept_associations (
            concept1 TEXT,
            concept2 TEXT,
            strength REAL,
            last_update REAL,
            PRIMARY KEY (concept1, concept2)
        )
        """)
        
        # СОВМЕСТИМОСТЬ: создаем старые таблицы для обратной совместимости
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            timestamp REAL,
            user_input TEXT,
            field_output TEXT,
            metrics TEXT,
            transformer_config TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_frequencies (
            word TEXT PRIMARY KEY,
            count INTEGER DEFAULT 1
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bigrams (
            id INTEGER PRIMARY KEY,
            w1 TEXT,
            w2 TEXT,
            count INTEGER DEFAULT 1,
            UNIQUE(w1, w2)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_first_contact (
            user_id TEXT PRIMARY KEY,
            first_contact_time REAL,
            template_phase_completed INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
        conn.close()
        
    def load_memories_to_cache(self):
        """Загружает воспоминания в кеш и индексы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memory_entries ORDER BY importance DESC LIMIT 1000")
        rows = cursor.fetchall()
        
        for row in rows:
            entry = MemoryEntry(
                id=row[0],
                content=row[1], 
                context=row[2],
                timestamp=row[3],
                importance=row[4],
                access_count=row[5],
                last_access=row[6],
                associations=json.loads(row[7]) if row[7] else []
            )
            
            self.memory_cache[entry.id] = entry
            self.semantic_index.index_entry(entry)
            
        # Загружаем ассоциации
        cursor.execute("SELECT concept1, concept2, strength FROM concept_associations")
        assoc_rows = cursor.fetchall()
        
        for concept1, concept2, strength in assoc_rows:
            self.associative_network.associations[concept1][concept2] = strength
            
        conn.close()
        
        # МИГРАЦИЯ: загружаем старые данные если новых нет
        if len(self.memory_cache) == 0:
            self.migrate_old_memory_data()
        
        print(f"[FieldMemory] Загружено {len(self.memory_cache)} воспоминаний")
        
        # Добавляем совместимость с основной Field
        self.word_frequencies = defaultdict(int)
        self.bigram_transitions = defaultdict(lambda: defaultdict(int))
        try:
            from field_metrics import VerbGraph
            self.verb_graph = VerbGraph()
        except ImportError:
            self.verb_graph = None
            
        # Загружаем word_frequencies и bigrams
        self.load_compatibility_data()
        
    def store_memory(self, content: str, context: str = "", importance: float = 1.0, 
                    associations: List[str] = None) -> str:
        """Сохраняет новое воспоминание"""
        with self.memory_lock:
            memory_id = f"mem_{int(time.time() * 1000000)}"
            
            entry = MemoryEntry(
                id=memory_id,
                content=content,
                context=context,
                timestamp=time.time(),
                importance=importance,
                associations=associations or []
            )
            
            # Сохраняем в кеш и индекс
            self.memory_cache[memory_id] = entry
            self.semantic_index.index_entry(entry)
            self.recent_memories.append(memory_id)
            
            # Создаем ассоциации
            self._create_associations(entry)
            
            # Сохраняем в базу
            self._save_entry_to_db(entry)
            
            print(f"[FieldMemory] Сохранено воспоминание {memory_id}")
            return memory_id
            
    def _create_associations(self, entry: MemoryEntry):
        """Создает ассоциации для нового воспоминания"""
        words = self.semantic_index._extract_words(entry.content + " " + entry.context)
        
        # Создаем ассоциации между словами в воспоминании
        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i != j:
                    distance = abs(i - j)
                    strength = 1.0 / (1 + distance * 0.1)  # Ближние слова связаны сильнее
                    self.associative_network.add_association(word1, word2, strength * entry.importance)
                    
    def _save_entry_to_db(self, entry: MemoryEntry):
        """Сохраняет запись в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO memory_entries 
        (id, content, context, timestamp, importance, access_count, last_access, associations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.content,
            entry.context, 
            entry.timestamp,
            entry.importance,
            entry.access_count,
            entry.last_access,
            json.dumps(entry.associations)
        ))
        
        conn.commit()
        conn.close()
        
    def recall_memories(self, query: str, limit: int = 5, min_importance: float = 0.1) -> List[MemoryEntry]:
        """Вспоминает релевантные воспоминания"""
        with self.memory_lock:
            # Семантический поиск
            matching_ids = self.semantic_index.search(query, limit * 3)
            
            # Фильтруем по важности и получаем записи
            relevant_memories = []
            for memory_id in matching_ids:
                if memory_id in self.memory_cache:
                    entry = self.memory_cache[memory_id]
                    if entry.importance >= min_importance:
                        relevant_memories.append(entry)
                        
            # Сортируем по релевантности (важность + свежесть + частота доступа)
            def relevance_score(entry: MemoryEntry) -> float:
                recency = 1.0 / (1 + (time.time() - entry.timestamp) / 86400)  # Свежесть в днях
                access_freq = math.log(1 + entry.access_count) / 10
                return entry.importance * 0.5 + recency * 0.3 + access_freq * 0.2
                
            relevant_memories.sort(key=relevance_score, reverse=True)
            
            # Обновляем статистику доступа
            for entry in relevant_memories[:limit]:
                entry.access_count += 1
                entry.last_access = time.time()
                self._save_entry_to_db(entry)
                
            return relevant_memories[:limit]
            
    def get_associative_context(self, query: str, depth: int = 2) -> List[str]:
        """Получает ассоциативный контекст для запроса"""
        words = self.semantic_index._extract_words(query)
        
        all_associations = set()
        
        # Первый уровень ассоциаций
        for word in words:
            related = self.associative_network.get_related_concepts(word, 3)
            for concept, strength in related:
                if strength > 0.5:  # Только сильные ассоциации
                    all_associations.add(concept)
                    
        # Второй уровень (ассоциации ассоциаций)
        if depth > 1:
            second_level = set()
            for concept in list(all_associations):
                related = self.associative_network.get_related_concepts(concept, 2)
                for concept2, strength in related:
                    if strength > 0.3:
                        second_level.add(concept2)
            all_associations.update(second_level)
            
        return list(all_associations)
        
    def consolidate_memories(self, threshold: float = 0.8):
        """Консолидирует похожие воспоминания"""
        with self.memory_lock:
            memories = list(self.memory_cache.values())
            to_merge = []
            
            # Находим похожие воспоминания
            for i, mem1 in enumerate(memories):
                for j, mem2 in enumerate(memories[i+1:], i+1):
                    similarity = self._calculate_similarity(mem1, mem2)
                    if similarity > threshold:
                        to_merge.append((mem1, mem2, similarity))
                        
            # Объединяем похожие воспоминания
            for mem1, mem2, similarity in to_merge:
                merged_entry = self._merge_memories(mem1, mem2)
                
                # Удаляем старые записи
                if mem1.id in self.memory_cache:
                    del self.memory_cache[mem1.id]
                if mem2.id in self.memory_cache:
                    del self.memory_cache[mem2.id]
                    
                # Добавляем объединенную
                self.memory_cache[merged_entry.id] = merged_entry
                self.semantic_index.index_entry(merged_entry)
                self._save_entry_to_db(merged_entry)
                
            if to_merge:
                print(f"[FieldMemory] Консолидировано {len(to_merge)} пар воспоминаний")
                
    def _calculate_similarity(self, mem1: MemoryEntry, mem2: MemoryEntry) -> float:
        """Рассчитывает схожесть двух воспоминаний"""
        words1 = set(self.semantic_index._extract_words(mem1.content))
        words2 = set(self.semantic_index._extract_words(mem2.content))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # Учитываем временную близость
        time_diff = abs(mem1.timestamp - mem2.timestamp)
        time_similarity = 1.0 / (1 + time_diff / 3600)  # Часы
        
        return jaccard * 0.7 + time_similarity * 0.3
        
    def _merge_memories(self, mem1: MemoryEntry, mem2: MemoryEntry) -> MemoryEntry:
        """Объединяет два воспоминания"""
        merged_content = f"{mem1.content} | {mem2.content}"
        merged_context = f"{mem1.context} | {mem2.context}"
        
        return MemoryEntry(
            id=f"merged_{int(time.time() * 1000000)}",
            content=merged_content,
            context=merged_context,
            timestamp=max(mem1.timestamp, mem2.timestamp),
            importance=max(mem1.importance, mem2.importance),
            access_count=mem1.access_count + mem2.access_count,
            last_access=max(mem1.last_access, mem2.last_access),
            associations=list(set(mem1.associations + mem2.associations))
        )
        
    def forget_old_memories(self, age_threshold: float = 7 * 24 * 3600):  # 7 дней
        """Забывает старые неважные воспоминания"""
        with self.memory_lock:
            current_time = time.time()
            to_forget = []
            
            for memory_id, entry in self.memory_cache.items():
                age = current_time - entry.timestamp
                
                # Забываем если старое И неважное И редко используется
                if (age > age_threshold and 
                    entry.importance < 0.3 and 
                    entry.access_count < 2):
                    to_forget.append(memory_id)
                    
            # Удаляем забытые воспоминания
            for memory_id in to_forget:
                del self.memory_cache[memory_id]
                
            if to_forget:
                print(f"[FieldMemory] Забыто {len(to_forget)} старых воспоминаний")
                
    def get_conversation_context(self, current_input: str, session_id: str = None) -> str:
        """Получает контекст для текущего разговора"""
        # Вспоминаем релевантные воспоминания
        relevant_memories = self.recall_memories(current_input, limit=3)
        
        # Получаем ассоциативный контекст
        associations = self.get_associative_context(current_input, depth=1)
        
        # Формируем контекст
        context_parts = []
        
        if relevant_memories:
            context_parts.append("Релевантные воспоминания:")
            for mem in relevant_memories:
                context_parts.append(f"- {mem.content[:100]}...")
                
        if associations:
            context_parts.append(f"Ассоциации: {', '.join(associations[:10])}")
            
        return " ".join(context_parts) if context_parts else ""
        
    def learn_from_conversation(self, user_input: str, field_output: str, 
                              session_context: str = "", importance: float = None):
        """Обучается на основе разговора"""
        if importance is None:
            # Автоматически определяем важность
            importance = self._calculate_importance(user_input, field_output)
            
        # Сохраняем воспоминание о взаимодействии
        memory_content = f"Пользователь: {user_input} | Field: {field_output}"
        memory_id = self.store_memory(memory_content, session_context, importance)
        
        # Создаем ассоциации между концепциями в разговоре
        user_concepts = self.semantic_index._extract_words(user_input)
        field_concepts = self.semantic_index._extract_words(field_output)
        
        # Связываем концепции пользователя и Field
        for user_concept in user_concepts:
            for field_concept in field_concepts:
                self.associative_network.add_association(user_concept, field_concept, importance)
                
        return memory_id
        
    def _calculate_importance(self, user_input: str, field_output: str) -> float:
        """Автоматически рассчитывает важность взаимодействия"""
        # Базовая важность
        importance = 0.5
        
        # Увеличиваем важность для:
        # - Длинных сообщений (больше информации)
        if len(user_input) > 50:
            importance += 0.2
            
        # - Вопросов (требуют запоминания)
        if any(char in user_input for char in '?'):
            importance += 0.1
            
        # - Личной информации
        personal_words = ['я', 'мне', 'мой', 'моя', 'мое', 'меня', 'себя']
        if any(word in user_input.lower().split() for word in personal_words):
            importance += 0.3
            
        # - Эмоциональных слов
        emotional_words = ['люблю', 'ненавижу', 'нравится', 'злой', 'грустный', 'счастливый']
        if any(word in user_input.lower() for word in emotional_words):
            importance += 0.2
            
        return min(1.0, importance)
        
    def periodic_maintenance(self):
        """Периодическое обслуживание памяти"""
        while True:
            try:
                time.sleep(3600)  # Каждый час
                
                # Консолидируем воспоминания
                self.consolidate_memories()
                
                # Забываем старые воспоминания
                self.forget_old_memories()
                
                # Ослабляем ассоциации
                self.associative_network.decay_associations()
                
                print("[FieldMemory] Периодическое обслуживание выполнено")
                
            except Exception as e:
                print(f"[FieldMemory:ERROR] Ошибка обслуживания: {e}")
                
    def start_maintenance(self):
        """Запускает периодическое обслуживание"""
        maintenance_thread = threading.Thread(target=self.periodic_maintenance, daemon=True)
        maintenance_thread.start()
        print("[FieldMemory] Периодическое обслуживание запущено")
        
    def get_memory_statistics(self) -> Dict:
        """Возвращает статистику памяти"""
        total_memories = len(self.memory_cache)
        
        if total_memories == 0:
            return {'total_memories': 0}
            
        importances = [mem.importance for mem in self.memory_cache.values()]
        access_counts = [mem.access_count for mem in self.memory_cache.values()]
        
        return {
            'total_memories': total_memories,
            'avg_importance': sum(importances) / len(importances),
            'max_importance': max(importances),
            'avg_access_count': sum(access_counts) / len(access_counts),
            'total_associations': sum(len(assocs) for assocs in self.associative_network.associations.values()),
            'recent_memories': len(self.recent_memories)
        }
    
    def migrate_old_memory_data(self):
        """Мигрирует данные из старых таблиц в новую систему памяти"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем есть ли старые данные
            cursor.execute("SELECT COUNT(*) FROM conversations")
            old_conversations = cursor.fetchone()[0]
            
            if old_conversations > 0:
                print(f"[FieldMemory] Мигрирую {old_conversations} старых разговоров...")
                
                # Загружаем старые разговоры
                cursor.execute("""
                    SELECT user_input, field_output, timestamp, session_id 
                    FROM conversations 
                    WHERE user_input IS NOT NULL AND field_output IS NOT NULL
                    ORDER BY timestamp DESC 
                    LIMIT 500
                """)
                
                for user_input, field_output, timestamp, session_id in cursor.fetchall():
                    # Создаем воспоминание из разговора
                    content = f"User: {user_input} | Field: {field_output}"
                    context = f"conversation_{session_id or 'unknown'}"
                    importance = 0.7  # Средняя важность для мигрированных данных
                    
                    memory_id = self.store_memory(content, context, importance)
                    
                print(f"[FieldMemory] Миграция завершена!")
                
            conn.close()
            
        except Exception as e:
            print(f"[FieldMemory] Ошибка миграции: {e}")
    
    def load_compatibility_data(self):
        """Загружает word_frequencies и bigrams для совместимости"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Загружаем частоты слов
            cursor.execute("SELECT word, count FROM word_frequencies")
            for word, count in cursor.fetchall():
                self.word_frequencies[word] = count
                
            # Загружаем биграммы  
            cursor.execute("SELECT w1, w2, count FROM bigrams")
            for w1, w2, count in cursor.fetchall():
                self.bigram_transitions[w1][w2] = count
                
            conn.close()
            
            words_count = len(self.word_frequencies)
            bigrams_count = sum(len(transitions) for transitions in self.bigram_transitions.values())
            if words_count > 0 or bigrams_count > 0:
                print(f"[FieldMemory] Загружена совместимость: {words_count} слов, {bigrams_count} биграмм")
                
        except Exception as e:
            print(f"[FieldMemory] Ошибка загрузки совместимости: {e}")

# Интеграция будет добавлена позже
# TODO: Интегрировать с основной Field системой

# Функция интеграции будет добавлена позже

def test_memory_system():
    """Тестирование системы памяти"""
    print("=== NICOLE MEMORY SYSTEM TEST ===")
    
    memory_core = FieldMemoryCore()
    
    # Тест 1: Сохранение воспоминаний
    print("\\n--- Тест сохранения ---")
    mem1 = memory_core.store_memory("Пользователь любит кофе", "разговор о предпочтениях", 0.8)
    mem2 = memory_core.store_memory("Обсуждали погоду вчера", "casual разговор", 0.3)
    mem3 = memory_core.store_memory("Пользователь работает программистом", "личная информация", 0.9)
    
    # Тест 2: Поиск воспоминаний
    print("\\n--- Тест поиска ---")
    results = memory_core.recall_memories("кофе программист", limit=3)
    for mem in results:
        print(f"Найдено: {mem.content} (важность: {mem.importance:.2f})")
        
    # Тест 3: Ассоциативный контекст
    print("\\n--- Тест ассоциаций ---")
    associations = memory_core.get_associative_context("работа кофе")
    print(f"Ассоциации: {associations[:10]}")
    
    # Тест 4: Симуляция разговора
    print("\\n--- Тест симуляции разговора ---")
    
    test_conversations = [
        ("Привет! Меня зовут Алекс", "Привет Алекс!"),
        ("Я работаю программистом", "Круто! Программирование интересная работа"),
        ("Люблю пить кофе по утрам", "Кофе - отличный способ начать день"), 
        ("Как дела?", "Хорошо, спасибо!"),
    ]
    
    for user_msg, field_response in test_conversations:
        memory_core.learn_from_conversation(user_msg, field_response, "test_session")
        print(f"Сохранено: {user_msg} -> {field_response}")
        
    # Проверяем поиск по сохраненным разговорам
    print("\\n--- Поиск по сохраненным разговорам ---")
    results = memory_core.recall_memories("работа программист", limit=2)
    for mem in results:
        print(f"Найдено: {mem.content[:100]}...")
    
    # Статистика
    stats = memory_core.get_memory_statistics()
    print(f"\\nСтатистика памяти:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
        
    print("\\n=== MEMORY TEST COMPLETED ===")

# === МЕТОДЫ СОВМЕСТИМОСТИ С ОСНОВНОЙ NICOLE ===

def add_compatibility_methods():
    """Добавляет методы совместимости к FieldMemoryCore"""
    
    def update_word_frequencies(self, text: str):
        words = text.lower().split()
        for word in words:
            self.word_frequencies[word] += 1
    
    def update_bigrams(self, text: str):
        words = text.lower().split()
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            self.bigram_transitions[w1][w2] += 1
    
    def log_conversation(self, session_id: str, user_input: str, field_output: str, 
                        metrics: dict, transformer_config: dict):
        conversation_content = f"User: {user_input} | Field: {field_output}"
        self.store_memory(content=conversation_content, context=f"Session: {session_id}", importance=1.0)
        self.update_word_frequencies(user_input)
        self.update_word_frequencies(field_output)
        self.update_bigrams(user_input)
        self.update_bigrams(field_output)
    
    def log_transformer_lifecycle(self, transformer_id: str, session_id: str, architecture: dict, creation_time: float, death_time: float = None):
        action = "died" if death_time else "created"
        lifecycle_content = f"Transformer {transformer_id} {action}"
        self.store_memory(content=lifecycle_content, context=f"Session: {session_id}", importance=0.8)
    
    def is_response_repetitive(self, response: str, threshold: float = 0.8) -> bool:
        return False
    
    def get_semantic_candidates(self, word: str, distance_percent: float = 0.5) -> List[str]:
        """Получает семантические кандидаты (совместимость с field.py)"""
        # Конвертируем distance_percent в limit для совместимости
        limit = max(5, int(distance_percent * 20))  # 0.5 -> 10, 0.7 -> 14
        candidates = []
        if word in self.associative_network.associations:
            candidates = list(self.associative_network.associations[word].keys())[:limit]
        return candidates if candidates else [word]
    
    # Добавляем методы к классу
    FieldMemoryCore.update_word_frequencies = update_word_frequencies
    FieldMemoryCore.update_bigrams = update_bigrams
    FieldMemoryCore.log_conversation = log_conversation
    FieldMemoryCore.log_transformer_lifecycle = log_transformer_lifecycle
    FieldMemoryCore.is_response_repetitive = is_response_repetitive
    FieldMemoryCore.get_semantic_candidates = get_semantic_candidates

# Автоматически добавляем совместимость
add_compatibility_methods()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_memory_system()
    else:
        print("Field Memory System готова к работе")
        print("Для тестирования запустите: python3 field_memory.py test")
