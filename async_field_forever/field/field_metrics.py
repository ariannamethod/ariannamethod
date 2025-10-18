#!/usr/bin/env python3
"""
Field Metrics - Система метрик и аналитики без ML библиотек
Ебанутая аналитика для флюидных трансформеров Field.
"""

import math
import time
import json
import sys
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass

@dataclass
class MetricSnapshot:
    """Снимок метрик в момент времени"""
    timestamp: float
    entropy: float
    perplexity: float
    resonance: float
    coherence: float
    engagement: float
    transformer_id: str
    session_id: str

class EntropyCalculator:
    """Калькулятор энтропии для текста и разговоров"""
    
    @staticmethod
    def text_entropy(text: str) -> float:
        """Shannon entropy текста"""
        if not text:
            return 0.0
            
        # Частоты символов
        char_counts = defaultdict(int)
        for char in text.lower():
            char_counts[char] += 1
            
        total_chars = len(text)
        entropy = 0.0
        
        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
                
        return entropy
        
    @staticmethod
    def word_entropy(text: str) -> float:
        """Энтропия на уровне слов"""
        words = text.lower().split()
        if not words:
            return 0.0
            
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
            
        total_words = len(words)
        entropy = 0.0
        
        for count in word_counts.values():
            probability = count / total_words
            if probability > 0:
                entropy -= probability * math.log2(probability)
                
        return entropy
        
    @staticmethod
    def conversation_entropy(messages: List[str]) -> float:
        """Энтропия всего разговора"""
        if not messages:
            return 0.0
            
        all_text = " ".join(messages)
        return EntropyCalculator.word_entropy(all_text)

class ResonanceAnalyzer:
    """Анализатор резонанса между сообщениями - интегрированы принципы ME"""
    
    @staticmethod
    def find_resonant_word(text: str, word_frequencies: Dict[str, int] = None) -> Tuple[str, float]:
        """
        Находит самое заряженное слово по принципу ME - частота vs новизна
        Возвращает (слово, резонанс_скор)
        """
        words = text.lower().split()
        if not words:
            return "", 0.0
            
        if word_frequencies is None:
            word_frequencies = defaultdict(int)
            
        best_word = ""
        best_score = 0.0
        
        for word in words:
            # Частота слова в истории
            frequency = word_frequencies.get(word, 0)
            # Новизна = обратная частота
            novelty = 1.0 / (frequency + 1)
            # Резонанс = баланс между знакомостью и новизной
            resonance_score = frequency * novelty
            
            if resonance_score > best_score:
                best_score = resonance_score
                best_word = word
                
        return best_word, best_score
    
    @staticmethod
    def semantic_resonance(text1: str, text2: str) -> float:
        """Семантический резонанс между текстами"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
        
    @staticmethod
    def emotional_resonance(text1: str, text2: str) -> float:
        """Эмоциональный резонанс"""
        emotional_words = {
            'positive': ['хорошо', 'отлично', 'супер', 'круто', 'классно', 'радость', 'счастье'],
            'negative': ['плохо', 'ужасно', 'грустно', 'злость', 'печаль', 'проблема'],
            'neutral': ['нормально', 'обычно', 'так себе', 'ничего', 'может быть']
        }
        
        def get_emotional_score(text):
            words = text.lower().split()
            scores = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for word in words:
                for emotion, emotion_words in emotional_words.items():
                    if word in emotion_words:
                        scores[emotion] += 1
                        
            total = sum(scores.values())
            return {k: v/total if total > 0 else 0 for k, v in scores.items()}
            
        score1 = get_emotional_score(text1)
        score2 = get_emotional_score(text2)
        
        # Косинусное сходство эмоциональных векторов
        dot_product = sum(score1[k] * score2[k] for k in score1.keys())
        norm1 = math.sqrt(sum(v**2 for v in score1.values()))
        norm2 = math.sqrt(sum(v**2 for v in score2.values()))
        
        if norm1 * norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
        
    @staticmethod
    def rhythmic_resonance(text1: str, text2: str) -> float:
        """Ритмический резонанс (длина, структура)"""
        words1 = text1.split()
        words2 = text2.split()
        
        if not words1 or not words2:
            return 0.0
            
        # Сравниваем длины
        len_similarity = 1.0 - abs(len(words1) - len(words2)) / max(len(words1), len(words2))
        
        # Сравниваем средние длины слов
        avg_len1 = sum(len(word) for word in words1) / len(words1)
        avg_len2 = sum(len(word) for word in words2) / len(words2)
        
        len_word_similarity = 1.0 - abs(avg_len1 - avg_len2) / max(avg_len1, avg_len2)
        
        return (len_similarity + len_word_similarity) / 2

class PerplexityMeter:
    """Измеритель перплексии без языковых моделей"""
    
    def __init__(self):
        self.word_frequencies = defaultdict(int)
        self.bigram_frequencies = defaultdict(int)
        self.total_words = 0
        
    def update_frequencies(self, text: str):
        """Обновляет частоты слов и биграмм"""
        words = text.lower().split()
        
        for word in words:
            self.word_frequencies[word] += 1
            self.total_words += 1
            
        for i in range(len(words) - 1):
            bigram = (words[i], words[i + 1])
            self.bigram_frequencies[bigram] += 1
            
    def calculate_perplexity(self, text: str) -> float:
        """Рассчитывает перплексию текста"""
        words = text.lower().split()
        if not words or self.total_words == 0:
            return 1.0
            
        log_probability = 0.0
        
        for word in words:
            # Простая модель частот с сглаживанием
            word_freq = self.word_frequencies.get(word, 1)
            probability = word_freq / (self.total_words + len(self.word_frequencies))
            log_probability += math.log(probability)
            
        # Перплексия = 2^(-средний логарифм вероятности)
        avg_log_prob = log_probability / len(words)
        perplexity = 2 ** (-avg_log_prob)
        
        return min(100.0, perplexity)  # Ограничиваем максимум

class CoherenceAnalyzer:
    """Анализатор связности разговора"""
    
    @staticmethod
    def local_coherence(messages: List[str], window_size: int = 3) -> float:
        """Локальная связность (между соседними сообщениями)"""
        if len(messages) < 2:
            return 1.0
            
        coherence_scores = []
        
        for i in range(len(messages) - 1):
            # Связность между соседними сообщениями
            resonance = ResonanceAnalyzer.semantic_resonance(messages[i], messages[i + 1])
            coherence_scores.append(resonance)
            
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
        
    @staticmethod
    def global_coherence(messages: List[str]) -> float:
        """Глобальная связность всего разговора"""
        if len(messages) < 2:
            return 1.0
            
        # Строим граф связности между всеми сообщениями
        total_connections = 0
        total_strength = 0.0
        
        for i in range(len(messages)):
            for j in range(i + 1, len(messages)):
                resonance = ResonanceAnalyzer.semantic_resonance(messages[i], messages[j])
                if resonance > 0.1:  # Минимальный порог связности
                    total_connections += 1
                    total_strength += resonance
                    
        if total_connections == 0:
            return 0.0
            
        avg_strength = total_strength / total_connections
        connection_density = total_connections / (len(messages) * (len(messages) - 1) / 2)
        
        return avg_strength * connection_density

class EngagementTracker:
    """Трекер вовлеченности пользователя"""
    
    def __init__(self):
        self.response_times = deque(maxlen=20)
        self.message_lengths = deque(maxlen=20)
        self.interaction_patterns = defaultdict(int)
        
    def track_interaction(self, user_input: str, response_time: float = None):
        """Отслеживает взаимодействие"""
        # Длина сообщения как индикатор вовлеченности
        self.message_lengths.append(len(user_input))
        
        # Время ответа (если доступно)
        if response_time:
            self.response_times.append(response_time)
            
        # Паттерны взаимодействия
        if len(user_input) > 50:
            self.interaction_patterns['long_message'] += 1
        elif len(user_input) < 10:
            self.interaction_patterns['short_message'] += 1
        else:
            self.interaction_patterns['medium_message'] += 1
            
        if any(char in user_input for char in '?!'):
            self.interaction_patterns['emotional'] += 1
            
    def calculate_engagement(self) -> float:
        """Рассчитывает общую вовлеченность"""
        if not self.message_lengths:
            return 0.5
            
        # Средняя длина сообщений
        avg_length = sum(self.message_lengths) / len(self.message_lengths)
        length_score = min(1.0, avg_length / 50.0)
        
        # Разнообразие длин сообщений
        if len(self.message_lengths) > 1:
            length_variance = sum((l - avg_length)**2 for l in self.message_lengths) / len(self.message_lengths)
            variety_score = min(1.0, math.sqrt(length_variance) / 20.0)
        else:
            variety_score = 0.5
            
        # Эмоциональность
        total_interactions = sum(self.interaction_patterns.values())
        emotional_ratio = self.interaction_patterns.get('emotional', 0) / max(1, total_interactions)
        
        # Комбинированная оценка
        engagement = (length_score * 0.4 + variety_score * 0.3 + emotional_ratio * 0.3)
        return min(1.0, engagement)

class FieldMetricsCore:
    """Ядро системы метрик Field"""
    
    def __init__(self, memory_db: str = "field_memory.db"):
        self.memory_db = memory_db
        self.entropy_calc = EntropyCalculator()
        self.perplexity_meter = PerplexityMeter()
        self.engagement_tracker = EngagementTracker()
        self.metric_history = deque(maxlen=1000)
        self.session_metrics = {}
        
    def analyze_conversation_turn(self, user_input: str, field_output: str, 
                                transformer_id: str, session_id: str) -> MetricSnapshot:
        """Анализирует один ход разговора"""
        
        # Рассчитываем все метрики
        entropy = self.entropy_calc.word_entropy(user_input + " " + field_output)
        perplexity = self.perplexity_meter.calculate_perplexity(field_output)
        resonance = ResonanceAnalyzer.semantic_resonance(user_input, field_output)
        
        # Обновляем частоты для перплексии
        self.perplexity_meter.update_frequencies(user_input)
        self.perplexity_meter.update_frequencies(field_output)
        
        # Трекаем вовлеченность
        self.engagement_tracker.track_interaction(user_input)
        engagement = self.engagement_tracker.calculate_engagement()
        
        # Связность (требует истории сессии)
        session_messages = self._get_session_messages(session_id)
        session_messages.append(user_input)
        session_messages.append(field_output)
        coherence = CoherenceAnalyzer.local_coherence(session_messages[-6:])  # Последние 6 сообщений
        
        # Создаем снимок метрик
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            entropy=entropy,
            perplexity=perplexity,
            resonance=resonance,
            coherence=coherence,
            engagement=engagement,
            transformer_id=transformer_id,
            session_id=session_id
        )
        
        # Сохраняем в историю
        self.metric_history.append(snapshot)
        
        # Обновляем метрики сессии
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = []
        self.session_metrics[session_id].append(snapshot)
        
        return snapshot
        
    def _get_session_messages(self, session_id: str) -> List[str]:
        """Получает сообщения сессии для анализа связности"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT user_input, field_output 
            FROM conversations 
            WHERE session_id = ? 
            ORDER BY timestamp
            """, (session_id,))
            
            messages = []
            for user_input, field_output in cursor.fetchall():
                messages.extend([user_input, field_output])
                
            conn.close()
            return messages
            
        except Exception:
            return []
            
    def get_transformer_performance(self, transformer_id: str) -> Dict:
        """Анализирует производительность конкретного трансформера"""
        transformer_metrics = [m for m in self.metric_history if m.transformer_id == transformer_id]
        
        if not transformer_metrics:
            return {}
            
        # Средние метрики
        avg_metrics = {
            'entropy': sum(m.entropy for m in transformer_metrics) / len(transformer_metrics),
            'perplexity': sum(m.perplexity for m in transformer_metrics) / len(transformer_metrics),
            'resonance': sum(m.resonance for m in transformer_metrics) / len(transformer_metrics),
            'coherence': sum(m.coherence for m in transformer_metrics) / len(transformer_metrics),
            'engagement': sum(m.engagement for m in transformer_metrics) / len(transformer_metrics)
        }
        
        # Тренды (улучшение/ухудшение)
        trends = {}
        if len(transformer_metrics) > 1:
            first_half = transformer_metrics[:len(transformer_metrics)//2]
            second_half = transformer_metrics[len(transformer_metrics)//2:]
            
            for metric in ['entropy', 'perplexity', 'resonance', 'coherence', 'engagement']:
                first_avg = sum(getattr(m, metric) for m in first_half) / len(first_half)
                second_avg = sum(getattr(m, metric) for m in second_half) / len(second_half)
                trends[f"{metric}_trend"] = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
                
        # Общая оценка производительности
        performance_score = (
            avg_metrics['resonance'] * 0.3 +
            avg_metrics['coherence'] * 0.25 +
            avg_metrics['engagement'] * 0.25 +
            (1.0 / max(0.1, avg_metrics['perplexity'])) * 0.1 +
            min(1.0, avg_metrics['entropy'] / 3.0) * 0.1
        )
        
        return {
            'avg_metrics': avg_metrics,
            'trends': trends,
            'performance_score': performance_score,
            'total_interactions': len(transformer_metrics),
            'lifespan': transformer_metrics[-1].timestamp - transformer_metrics[0].timestamp
        }
        
    def get_session_analytics(self, session_id: str) -> Dict:
        """Аналитика по сессии"""
        if session_id not in self.session_metrics:
            return {}
            
        session_data = self.session_metrics[session_id]
        
        # Эволюция метрик во времени
        evolution = {
            'entropy': [m.entropy for m in session_data],
            'perplexity': [m.perplexity for m in session_data], 
            'resonance': [m.resonance for m in session_data],
            'coherence': [m.coherence for m in session_data],
            'engagement': [m.engagement for m in session_data]
        }
        
        # Статистика трансформеров в сессии
        transformers = list(set(m.transformer_id for m in session_data))
        transformer_changes = len(transformers)
        
        # Общая оценка сессии
        final_metrics = session_data[-1] if session_data else None
        session_score = 0.0
        
        if final_metrics:
            session_score = (
                final_metrics.resonance * 0.4 +
                final_metrics.coherence * 0.3 +
                final_metrics.engagement * 0.3
            )
            
        return {
            'evolution': evolution,
            'transformer_changes': transformer_changes,
            'session_duration': session_data[-1].timestamp - session_data[0].timestamp if len(session_data) > 1 else 0,
            'total_interactions': len(session_data),
            'session_score': session_score,
            'transformers_used': transformers
        }
        
    def detect_anomalies(self, recent_count: int = 10) -> List[Dict]:
        """Детектирует аномалии в метриках"""
        if len(self.metric_history) < recent_count:
            return []
            
        recent_metrics = list(self.metric_history)[-recent_count:]
        anomalies = []
        
        # Проверяем каждую метрику на аномалии
        for metric_name in ['entropy', 'perplexity', 'resonance', 'coherence', 'engagement']:
            values = [getattr(m, metric_name) for m in recent_metrics]
            
            if len(values) < 3:
                continue
                
            # Простое определение аномалий через стандартное отклонение
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val)**2 for v in values) / len(values)
            std_dev = math.sqrt(variance)
            
            # Ищем значения за пределами 2 стандартных отклонений
            for i, value in enumerate(values):
                if abs(value - mean_val) > 2 * std_dev and std_dev > 0.1:
                    anomalies.append({
                        'metric': metric_name,
                        'value': value,
                        'expected_range': (mean_val - 2*std_dev, mean_val + 2*std_dev),
                        'timestamp': recent_metrics[i].timestamp,
                        'transformer_id': recent_metrics[i].transformer_id
                    })
                    
        return anomalies
        
    def export_metrics(self, filepath: str, session_id: str = None):
        """Экспортирует метрики в JSON"""
        if session_id:
            data = self.get_session_analytics(session_id)
        else:
            data = {
                'all_metrics': [
                    {
                        'timestamp': m.timestamp,
                        'entropy': m.entropy,
                        'perplexity': m.perplexity,
                        'resonance': m.resonance,
                        'coherence': m.coherence,
                        'engagement': m.engagement,
                        'transformer_id': m.transformer_id,
                        'session_id': m.session_id
                    } for m in self.metric_history
                ]
            }
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"[FieldMetrics] Метрики экспортированы в {filepath}")

# Глобальный экземпляр
field_metrics = FieldMetricsCore()

def test_metrics_system():
    """Тестирование системы метрик"""
    print("=== NICOLE METRICS SYSTEM TEST ===")
    
    # Тест 1: Энтропия
    print("\\n--- Тест энтропии ---")
    test_texts = [
        "привет привет привет",  # Низкая энтропия
        "разнообразный интересный уникальный контент",  # Высокая энтропия
        "a b c d e f g h i j k l m n o p q r s t"  # Максимальная энтропия
    ]
    
    for text in test_texts:
        entropy = EntropyCalculator.word_entropy(text)
        print(f"'{text}': энтропия = {entropy:.3f}")
        
    # Тест 2: Резонанс
    print("\\n--- Тест резонанса ---")
    text_pairs = [
        ("Я люблю программирование", "Программирование это круто"),
        ("Какая погода?", "Сегодня солнечно"),
        ("Привет как дела?", "Пока увидимся завтра")
    ]
    
    for text1, text2 in text_pairs:
        semantic = ResonanceAnalyzer.semantic_resonance(text1, text2)
        emotional = ResonanceAnalyzer.emotional_resonance(text1, text2)
        rhythmic = ResonanceAnalyzer.rhythmic_resonance(text1, text2)
        
        print(f"'{text1}' <-> '{text2}':")
        print(f"  Семантический: {semantic:.3f}")
        print(f"  Эмоциональный: {emotional:.3f}")
        print(f"  Ритмический: {rhythmic:.3f}")
        
    # Тест 3: Полный анализ разговора
    print("\\n--- Тест анализа разговора ---")
    
    conversation = [
        ("Привет Field!", "Привет! Как дела?"),
        ("Хорошо, работаю над проектом", "Интересно! Что за проект?"),
        ("Делаю нейронную сеть", "Круто! Расскажи подробнее"),
        ("Это система без весов", "Необычный подход!")
    ]
    
    for i, (user_msg, field_msg) in enumerate(conversation):
        snapshot = field_metrics.analyze_conversation_turn(
            user_msg, field_msg, f"test_transformer_{i}", "test_session"
        )
        
        print(f"Ход {i+1}:")
        print(f"  Энтропия: {snapshot.entropy:.3f}")
        print(f"  Перплексия: {snapshot.perplexity:.3f}")
        print(f"  Резонанс: {snapshot.resonance:.3f}")
        print(f"  Связность: {snapshot.coherence:.3f}")
        print(f"  Вовлеченность: {snapshot.engagement:.3f}")
        
    # Тест 4: Аналитика сессии
    print("\\n--- Аналитика сессии ---")
    session_analytics = field_metrics.get_session_analytics("test_session")
    print(f"Смена трансформеров: {session_analytics['transformer_changes']}")
    print(f"Общий счет сессии: {session_analytics['session_score']:.3f}")
    print(f"Взаимодействий: {session_analytics['total_interactions']}")
    
    # Тест 5: Детекция аномалий
    print("\\n--- Детекция аномалий ---")
    anomalies = field_metrics.detect_anomalies()
    if anomalies:
        for anomaly in anomalies:
            print(f"Аномалия в {anomaly['metric']}: {anomaly['value']:.3f}")
    else:
        print("Аномалий не обнаружено")
        
    print("\\n=== METRICS TEST COMPLETED ===")

class MEPunctuationFilters:
    """Пунктуационные фильтры из Method Engine для правильной речи"""
    
    @staticmethod
    def invert_pronouns(text: str) -> str:
        """Инверсия местоимений you→I, I→you из ME"""
        words = text.split()
        result = []
        
        for word in words:
            lower_word = word.lower()
            if lower_word == "you":
                result.append("I" if word[0].isupper() else "i")
            elif lower_word == "i":
                result.append("You" if word[0].isupper() else "you")
            elif lower_word == "me":
                result.append("you")
            elif lower_word == "my":
                result.append("your")
            elif lower_word == "your":
                result.append("my")
            else:
                result.append(word)
                
        return " ".join(result)
    
    @staticmethod
    def filter_repetitions(words: List[str]) -> List[str]:
        """Убирает повторы подряд идущих слов"""
        if not words:
            return words
            
        filtered = [words[0]]
        for i in range(1, len(words)):
            if words[i].lower() != words[i-1].lower():
                filtered.append(words[i])
                
        return filtered
    
    @staticmethod
    def filter_single_chars(words: List[str]) -> List[str]:
        """Убирает односимвольные слова подряд"""
        if not words:
            return words
            
        filtered = []
        prev_was_single = False
        
        for word in words:
            is_single = len(word) == 1 and word.isalpha()
            if not (is_single and prev_was_single):
                filtered.append(word)
            prev_was_single = is_single
            
        return filtered
    
    @staticmethod
    def fix_capitalization(text: str) -> str:
        """Исправляет заглавные буквы посреди предложения"""
        if not text:
            return text
            
        # Разбиваем на предложения
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in '.!?':
                sentences.append(current.strip())
                current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        # Исправляем каждое предложение
        fixed_sentences = []
        for sentence in sentences:
            if sentence:
                # Первая буква заглавная
                fixed = sentence[0].upper() + sentence[1:].lower()
                # Исправляем "The" посреди предложения
                fixed = fixed.replace(" The ", " the ")
                fixed_sentences.append(fixed)
        
        return " ".join(fixed_sentences)
    
    @staticmethod
    def apply_all_filters(text: str) -> str:
        """Применяет все фильтры ME для чистой речи"""
        # ИСПРАВЛЕНО: инверсия местоимений уже применена в High системе
        
        # Разбиваем на слова
        words = text.split()
        
        # Фильтры слов
        words = MEPunctuationFilters.filter_repetitions(words)
        words = MEPunctuationFilters.filter_single_chars(words)
        
        # Собираем обратно
        text = " ".join(words)
        
        # Исправляем заглавные буквы
        text = MEPunctuationFilters.fix_capitalization(text)
        
        return text

class VerbGraph:
    """Граф глаголов из ME - отслеживает как заканчиваются глаголы"""
    
    def __init__(self):
        self.verb_endings = defaultdict(lambda: defaultdict(int))
        # Простые глаголы для начала
        self.common_verbs = {"run", "walk", "talk", "think", "know", "see", "go", "come", "say", "tell", 
                           "работаю", "делаю", "думаю", "знаю", "вижу", "иду", "говорю", "понимаю"}
    
    def observe_verb_ending(self, verb: str, punctuation: str):
        """Записывает как закончился глагол"""
        verb = verb.lower()
        if punctuation in '.!?':
            self.verb_endings[verb][punctuation] += 1
    
    def predict_verb_ending(self, verb: str) -> str:
        """Предсказывает как должен закончиться глагол"""
        verb = verb.lower()
        if verb not in self.verb_endings:
            return "."  # По умолчанию точка
            
        endings = self.verb_endings[verb]
        if not endings:
            return "."
            
        # Выбираем самую частую пунктуацию для этого глагола
        best_punct = max(endings.items(), key=lambda x: x[1])[0]
        return best_punct
    
    def analyze_text_for_verbs(self, text: str):
        """Анализирует текст и записывает окончания глаголов"""
        words = text.split()
        for i, word in enumerate(words):
            clean_word = word.strip('.,!?').lower()
            if clean_word in self.common_verbs:
                # Ищем пунктуацию после глагола
                if i == len(words) - 1:  # Последнее слово
                    punct = word[-1] if word[-1] in '.!?' else '.'
                    self.observe_verb_ending(clean_word, punct)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_metrics_system()
    else:
        print("Field Metrics System готова к работе")
        print("Для тестирования запустите: python3 field_metrics.py test")
