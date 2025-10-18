"""
Field AMLK Integration Module
Интеграция Field с Arianna Method Linux Kernel через letsgo.py

Field живет ВНУТРИ AMLK как операционной системы.
AMLK предоставляет системные функции через letsgo.py терминал.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
import threading
import queue
import subprocess

# Добавляем AMLK в path для импорта
AMLK_PATH = Path(__file__).parent / "AMLK"
sys.path.insert(0, str(AMLK_PATH))

class FieldAMLKBridge:
    """
    Мост между Field и AMLK операционной системой
    Field работает ВНУТРИ AMLK, используя ее системные вызовы
    """
    
    def __init__(self):
        self.amlk_process = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        self.log_file = "amlk_system.log"
        
    def start_amlk_os(self):
        """Запуск AMLK операционной системы"""
        try:
            # Запускаем letsgo.py как системный процесс
            self.amlk_process = subprocess.Popen(
                [sys.executable, str(AMLK_PATH / "letsgo.py")],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.is_running = True
            
            # Запускаем мониторинг вывода в отдельном потоке
            self._start_output_monitor()
            
            return True
        except Exception as e:
            # Log error instead of user output
            self._log_error(f"AMLK startup failed: {e}")
            return False
    
    def _start_output_monitor(self):
        """AMLK output monitoring in separate thread"""
        def monitor():
            while self.is_running and self.amlk_process:
                try:
                    line = self.amlk_process.stdout.readline()
                    if line:
                        self.response_queue.put(line.strip())
                except:
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def execute_system_command(self, command: str) -> Optional[str]:
        """
        Выполнение системной команды через AMLK
        Field использует это для системных операций
        """
        if not self.is_running or not self.amlk_process:
            return None
            
        try:
            # Отправляем команду в AMLK
            self.amlk_process.stdin.write(f"{command}\n")
            self.amlk_process.stdin.flush()
            
            # Ждем ответ (с таймаутом)
            try:
                response = self.response_queue.get(timeout=5.0)
                return response
            except queue.Empty:
                return None
                
        except Exception as e:
            print(f"Ошибка выполнения команды в AMLK: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе AMLK"""
        info = {}
        
        # Базовая информация через системные команды
        commands = {
            'pwd': 'pwd',
            'ls': 'ls -la',
            'memory': 'free -h' if os.name != 'nt' else 'dir',
            'processes': 'ps aux' if os.name != 'nt' else 'tasklist'
        }
        
        for key, cmd in commands.items():
            result = self.execute_system_command(cmd)
            if result:
                info[key] = result
                
        return info
    
    def field_system_call(self, operation: str, **kwargs) -> Any:
        """
        Системные вызовы Field через AMLK
        Это основной интерфейс для Field чтобы использовать ОС
        """
        if operation == "file_ops":
            # Файловые операции
            action = kwargs.get('action')
            path = kwargs.get('path')
            
            if action == 'read':
                return self.execute_system_command(f"cat {path}")
            elif action == 'write':
                content = kwargs.get('content', '')
                # Используем echo для записи (безопасно для простого контента)
                return self.execute_system_command(f'echo "{content}" > {path}')
            elif action == 'list':
                return self.execute_system_command(f"ls -la {path}")
                
        elif operation == "process_ops":
            # Процессы и память
            action = kwargs.get('action')
            
            if action == 'list':
                return self.execute_system_command("ps aux")
            elif action == 'memory':
                return self.execute_system_command("free -h")
                
        elif operation == "network_ops":
            # Сетевые операции
            action = kwargs.get('action')
            
            if action == 'status':
                return self.execute_system_command("netstat -an")
                
        return None
    
    def shutdown_amlk(self):
        """Корректное завершение AMLK"""
        if self.amlk_process:
            try:
                self.amlk_process.stdin.write("exit\n")
                self.amlk_process.stdin.flush()
                self.amlk_process.wait(timeout=5)
            except:
                self.amlk_process.terminate()
            finally:
                self.is_running = False
    
    def _log_info(self, message: str):
        """Логирование для системы, не для юзера"""
        with open(self.log_file, "a") as f:
            f.write(f"[AMLK:INFO] {message}\n")
    
    def _log_error(self, message: str):
        """Логирование ошибок для системы"""
        with open(self.log_file, "a") as f:
            f.write(f"[AMLK:ERROR] {message}\n")

# Глобальный экземпляр моста
_amlk_bridge = None

def get_amlk_bridge() -> FieldAMLKBridge:
    """Получение глобального экземпляра AMLK моста"""
    global _amlk_bridge
    if _amlk_bridge is None:
        _amlk_bridge = FieldAMLKBridge()
    return _amlk_bridge

def start_field_in_amlk():
    """
    Запуск Field внутри AMLK операционной системы
    Это основная функция интеграции
    """
    bridge = get_amlk_bridge()
    
    if bridge.start_amlk_os():
        # Получаем информацию о системе для внутреннего использования
        sys_info = bridge.get_system_info()
        bridge._log_info(f"AMLK OS active, sys_params: {len(sys_info)}")
        
        return bridge
    else:
        return None

if __name__ == "__main__":
    # Тестовый запуск интеграции
    bridge = start_field_in_amlk()
    
    if bridge:
        # Тест системных вызовов
        print("\n🔧 Тест системных операций:")
        
        # Тест файловых операций
        result = bridge.field_system_call("file_ops", action="list", path=".")
        print(f"Список файлов: {result}")
        
        # Тест процессов
        result = bridge.field_system_call("process_ops", action="memory")
        print(f"Память системы: {result}")
        
        # Завершение
        bridge.shutdown_amlk()
        print("🏁 AMLK корректно завершена")
