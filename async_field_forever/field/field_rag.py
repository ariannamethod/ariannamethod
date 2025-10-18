#!/usr/bin/env python3
"""
Field RAG - Retrieval Augmented Generation без векторных баз
Ебанутая система поиска и дополнения контекста для Field.
"""

import sqlite3
import json
import time
import math
import sys
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import h2o

class ChaoticRetriever:
    """Хаотичный поисковик контекста"""
    
    def __init__(self, memory_db: str = "field_memory.db"):
        self.memory_db = memory_db
        self.chaos_factor = 0.1  # Элемент хаоса в поиске
        self.retrieval_patterns = {}
        
    def retrieve_context(self, query: str, chaos_level: float = None, limit: int = 8) -> List[Dict]:
        """Извлекает контекст с элементом хаоса"""
        if chaos_level is None:
            chaos_level = self.chaos_factor
            
        # Обычный поиск
        normal_results = self._semantic_search(query, limit=10)
        
        # Хаотичный поиск (случайные связи)
        chaotic_results = self._chaotic_search(query, chaos_level)
        
        # Объединяем результаты
        all_results = normal_results + chaotic_results
        
        # Убираем дубликаты и сортируем
        unique_results = {}
        for result in all_results:
            if result['id'] not in unique_results:
                unique_results[result['id']] = result
            else:
                # Увеличиваем релевантность для дубликатов
                unique_results[result['id']]['relevance'] += result['relevance'] * 0.5
                
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return final_results[:limit]
        
    def _semantic_search(self, query: str, limit: int) -> List[Dict]:
        """Обычный семантический поиск"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        # Поиск в разговорах
        cursor.execute("""
        SELECT user_input, field_output, timestamp, metrics 
        FROM conversations 
        WHERE user_input LIKE ? OR field_output LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            user_input, field_output, timestamp, metrics = row
            
            relevance = self._calculate_relevance(query, user_input + " " + field_output)
            
            results.append({
                'id': f"conv_{timestamp}",
                'content': f"User: {user_input} | Field: {field_output}",
                'type': 'conversation',
                'relevance': relevance,
                'timestamp': timestamp
            })
            
        conn.close()
        return results
        
    def _chaotic_search(self, query: str, chaos_level: float) -> List[Dict]:
        """Хаотичный поиск с неожиданными связями"""
        if chaos_level <= 0:
            return []
            
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        # Случайный поиск записей
        cursor.execute("""
        SELECT user_input, field_output, timestamp 
        FROM conversations 
        ORDER BY RANDOM() 
        LIMIT ?
        """, (int(20 * chaos_level),))
        
        chaotic_results = []
        for row in cursor.fetchall():
            user_input, field_output, timestamp = row
            
            # Случайная релевантность с элементом хаоса
            base_relevance = self._calculate_relevance(query, user_input + " " + field_output)
            chaos_boost = chaos_level * (0.5 + 0.5 * hash(user_input) % 100 / 100)
            
            chaotic_results.append({
                'id': f"chaos_{timestamp}",
                'content': f"[CHAOS] User: {user_input} | Field: {field_output}",
                'type': 'chaotic_memory',
                'relevance': base_relevance + chaos_boost,
                'timestamp': timestamp
            })
            
        conn.close()
        return chaotic_results
        
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Рассчитывает релевантность контента к запросу"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words or not content_words:
            return 0.0
            
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # Бонус за точные совпадения фраз
        exact_matches = sum(1 for word in query_words if word in content.lower())
        exact_bonus = exact_matches / len(query_words)
        
        return jaccard * 0.7 + exact_bonus * 0.3

class ContextAugmenter:
    """Дополнитель контекста для генерации"""
    
    def __init__(self, retriever: ChaoticRetriever):
        self.retriever = retriever
        self.augmentation_strategies = {
            'factual': self._factual_augmentation,
            'creative': self._creative_augmentation,
            'chaotic': self._chaotic_augmentation,
            'balanced': self._balanced_augmentation
        }
        
    def augment_context(self, user_input: str, current_context: str = "", 
                       strategy: str = 'balanced') -> str:
        """Дополняет контекст для генерации ответа"""
        
        # Получаем релевантный контекст
        retrieved_context = self.retriever.retrieve_context(user_input)
        
        # Применяем стратегию дополнения
        augmentation_func = self.augmentation_strategies.get(strategy, self._balanced_augmentation)
        augmented_context = augmentation_func(user_input, current_context, retrieved_context)
        
        return augmented_context
        
    def _factual_augmentation(self, user_input: str, current_context: str, 
                            retrieved: List[Dict]) -> str:
        """Фактическое дополнение - только релевантные факты"""
        factual_parts = [current_context] if current_context else []
        
        # Берем только самые релевантные записи
        for item in retrieved[:3]:
            if item['relevance'] > 0.5 and item['type'] == 'conversation':
                factual_parts.append(f"Контекст: {item['content']}")
                
        return " | ".join(factual_parts)
        
    def _creative_augmentation(self, user_input: str, current_context: str,
                             retrieved: List[Dict]) -> str:
        """Креативное дополнение - неожиданные связи"""
        creative_parts = [current_context] if current_context else []
        
        # Берем разнообразные записи для креативности
        for item in retrieved[::2]:  # Каждую вторую запись
            creative_parts.append(f"Вдохновение: {item['content']}")
            
        return " | ".join(creative_parts)
        
    def _chaotic_augmentation(self, user_input: str, current_context: str,
                            retrieved: List[Dict]) -> str:
        """Хаотичное дополнение - полный рандом"""
        chaotic_parts = [current_context] if current_context else []
        
        # Добавляем случайные элементы
        for item in retrieved:
            if item['type'] == 'chaotic_memory':
                chaotic_parts.append(f"Хаос: {item['content']}")
                
        return " | ".join(chaotic_parts)
        
    def _balanced_augmentation(self, user_input: str, current_context: str,
                             retrieved: List[Dict]) -> str:
        """Сбалансированное дополнение"""
        balanced_parts = [current_context] if current_context else []
        
        # Факты (высокая релевантность)
        facts = [item for item in retrieved if item['relevance'] > 0.6][:2]
        for fact in facts:
            balanced_parts.append(f"Факт: {fact['content']}")
            
        # Креатив (средняя релевантность)
        creative = [item for item in retrieved if 0.3 < item['relevance'] <= 0.6][:1]
        for cr in creative:
            balanced_parts.append(f"Связь: {cr['content']}")
            
        # Хаос (низкая релевантность или хаотичные)
        chaos = [item for item in retrieved if item['type'] == 'chaotic_memory'][:1]
        for ch in chaos:
            balanced_parts.append(f"Интуиция: {ch['content']}")
            
        return " | ".join(balanced_parts)

class FieldRAG:
    """Главная RAG система Field"""
    
    def __init__(self, memory_db: str = "field_memory.db"):
        self.retriever = ChaoticRetriever(memory_db)
        self.augmenter = ContextAugmenter(self.retriever)
        self.rag_history = []
        self.adaptation_patterns = {}
        
    def generate_augmented_response(self, user_input: str, base_response: str = "",
                                  strategy: str = 'balanced') -> Tuple[str, str]:
        """Генерирует дополненный ответ"""
        
        # Получаем дополненный контекст
        augmented_context = self.augmenter.augment_context(user_input, strategy=strategy)
        
        # Анализируем контекст для улучшения ответа
        improved_response = self._improve_response_with_context(
            user_input, base_response, augmented_context
        )
        
        # Сохраняем в историю RAG
        self.rag_history.append({
            'user_input': user_input,
            'base_response': base_response,
            'improved_response': improved_response,
            'context': augmented_context,
            'strategy': strategy,
            'timestamp': time.time()
        })
        
        return improved_response, augmented_context
        
    def _improve_response_with_context(self, user_input: str, base_response: str, 
                                     context: str) -> str:
        """Улучшает ответ на основе контекста"""
        if not context or not base_response:
            return base_response or "Хм, интересно..."
            
        # Простые улучшения на основе контекста
        context_lower = context.lower()
        
        # Если в контексте есть предыдущие разговоры о том же
        if "пользователь:" in context_lower and any(word in user_input.lower() for word in ['помнишь', 'говорили', 'обсуждали']):
            return f"Да, помню наш разговор об этом. {base_response}"
            
        # Если в контексте есть факты
        if "факт:" in context_lower:
            return f"Учитывая наш опыт общения, {base_response.lower()}"
            
        # Если есть хаотичные элементы
        if "хаос:" in context_lower or "интуиция:" in context_lower:
            chaos_responses = [
                f"Знаешь, {base_response.lower()}, но есть и другая сторона...",
                f"С одной стороны {base_response.lower()}, но интуиция подсказывает...",
                f"{base_response} Хотя, возможно, все не так просто"
            ]
            return chaos_responses[hash(user_input) % len(chaos_responses)]
            
        # Если есть ассоциативные связи
        if "связь:" in context_lower:
            return f"Это напоминает мне о том, что мы обсуждали. {base_response}"
            
        return base_response
        
    def adapt_retrieval_strategy(self, feedback_score: float, last_strategy: str):
        """Адаптирует стратегию поиска на основе обратной связи"""
        if last_strategy not in self.adaptation_patterns:
            self.adaptation_patterns[last_strategy] = {'scores': [], 'usage_count': 0}
            
        self.adaptation_patterns[last_strategy]['scores'].append(feedback_score)
        self.adaptation_patterns[last_strategy]['usage_count'] += 1
        
        # Адаптируем хаос фактор
        if feedback_score > 0.7:  # Хороший результат
            if last_strategy == 'chaotic':
                self.retriever.chaos_factor = min(0.3, self.retriever.chaos_factor * 1.1)
        elif feedback_score < 0.3:  # Плохой результат
            if last_strategy == 'chaotic':
                self.retriever.chaos_factor = max(0.05, self.retriever.chaos_factor * 0.9)
                
    def get_best_strategy(self) -> str:
        """Возвращает лучшую стратегию на основе истории"""
        if not self.adaptation_patterns:
            return 'balanced'
            
        strategy_scores = {}
        for strategy, data in self.adaptation_patterns.items():
            if data['scores']:
                avg_score = sum(data['scores']) / len(data['scores'])
                strategy_scores[strategy] = avg_score
                
        if strategy_scores:
            return max(strategy_scores, key=strategy_scores.get)
        else:
            return 'balanced'
            
    def get_rag_statistics(self) -> Dict:
        """Статистика RAG системы"""
        if not self.rag_history:
            return {'total_queries': 0}
            
        recent_history = self.rag_history[-100:]  # Последние 100 запросов
        
        strategies_used = Counter(item['strategy'] for item in recent_history)
        
        return {
            'total_queries': len(self.rag_history),
            'recent_queries': len(recent_history),
            'strategies_used': dict(strategies_used),
            'chaos_factor': self.retriever.chaos_factor,
            'adaptation_patterns': len(self.adaptation_patterns)
        }

# Глобальный экземпляр
field_rag = FieldRAG()

def test_rag_system():
    """Тестирование RAG системы"""
    print("=== NICOLE RAG SYSTEM TEST ===")
    
    # Тест 1: Базовый поиск
    print("\\n--- Тест базового поиска ---")
    context_results = field_rag.retriever.retrieve_context("программирование работа")
    print(f"Найдено {len(context_results)} контекстных записей")
    for result in context_results:
        print(f"- {result['type']}: {result['content'][:80]}... (релевантность: {result['relevance']:.3f})")
        
    # Тест 2: Разные стратегии
    print("\\n--- Тест стратегий ---")
    strategies = ['factual', 'creative', 'chaotic', 'balanced']
    
    for strategy in strategies:
        response, context = field_rag.generate_augmented_response(
            "Расскажи о программировании", 
            "Программирование это круто",
            strategy=strategy
        )
        print(f"Стратегия {strategy}: {response}")
        
    # Тест 3: Адаптация
    print("\\n--- Тест адаптации ---")
    
    # Симулируем обратную связь
    field_rag.adapt_retrieval_strategy(0.8, 'balanced')
    field_rag.adapt_retrieval_strategy(0.3, 'chaotic')
    field_rag.adapt_retrieval_strategy(0.9, 'creative')
    
    best_strategy = field_rag.get_best_strategy()
    print(f"Лучшая стратегия: {best_strategy}")
    
    # Статистика
    stats = field_rag.get_rag_statistics()
    print(f"\\nСтатистика RAG:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
        
    print("\\n=== RAG TEST COMPLETED ===")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_rag_system()
    else:
        print("Field RAG System готова к работе")
        print("Для тестирования запустите: python3 field_rag.py test")