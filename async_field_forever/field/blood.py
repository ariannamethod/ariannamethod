#!/usr/bin/env python3
"""
BLOOD.PY - The Blood of Nicole System
Низкоуровневый интерпретатор C для контроля железа

Nicole использует blood.py для:
- Прямого управления памятью
- Контроля системных процессов  
- Запуска C скриптов в трансформерах
- Нативной компиляции критического кода

Философия: C - это кровь системы, прямой контроль над железом
"""

import os
import sys
import subprocess
import tempfile
import threading
import ctypes
import mmap
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import time
try:
    import psutil
except ImportError:
    # Python 3.7 совместимость - psutil опционален
    psutil = None

# Добавляем nicole2c в путь для Clang компонентов
NICOLE2C_PATH = Path(__file__).parent / "nicole2c"
sys.path.insert(0, str(NICOLE2C_PATH))

class BloodMemoryManager:
    """
    Прямое управление памятью через Nicole
    Позволяет трансформерам контролировать выделение памяти
    """
    
    def __init__(self):
        self.allocated_blocks = {}
        self.memory_maps = {}
        self.total_allocated = 0
        
    def allocate_raw(self, size: int, alignment: int = 8) -> int:
        """Выделение сырой памяти с указанным выравниванием"""
        try:
            # Используем mmap для прямого контроля памяти
            memory_map = mmap.mmap(-1, size, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
            addr = ctypes.addressof(ctypes.c_char.from_buffer(memory_map))
            
            self.memory_maps[addr] = memory_map
            self.allocated_blocks[addr] = {
                'size': size,
                'alignment': alignment,
                'timestamp': time.time()
            }
            self.total_allocated += size
            
            return addr
        except Exception as e:
            raise RuntimeError(f"Blood memory allocation failed: {e}")
    
    def deallocate_raw(self, addr: int) -> bool:
        """Освобождение сырой памяти"""
        if addr in self.memory_maps:
            try:
                self.memory_maps[addr].close()
                size = self.allocated_blocks[addr]['size']
                
                del self.memory_maps[addr]
                del self.allocated_blocks[addr]
                self.total_allocated -= size
                
                return True
            except Exception:
                return False
        return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Статистика использования памяти"""
        return {
            'total_allocated': self.total_allocated,
            'blocks_count': len(self.allocated_blocks),
            'blocks_info': self.allocated_blocks.copy()
        }

class BloodProcessController:
    """
    Контроль системных процессов через Nicole
    Позволяет трансформерам управлять процессами напрямую
    """
    
    def __init__(self):
        self.controlled_processes = {}
        self.process_counter = 0
        
    def spawn_process(self, command: List[str], env: Dict[str, str] = None) -> int:
        """Создание процесса под контролем Nicole"""
        try:
            process = subprocess.Popen(
                command,
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.process_counter += 1
            process_id = self.process_counter
            
            self.controlled_processes[process_id] = {
                'process': process,
                'command': command,
                'created_at': time.time(),
                'status': 'running'
            }
            
            return process_id
        except Exception as e:
            raise RuntimeError(f"Blood process spawn failed: {e}")
    
    def kill_process(self, process_id: int, force: bool = False) -> bool:
        """Завершение процесса"""
        if process_id in self.controlled_processes:
            try:
                process = self.controlled_processes[process_id]['process']
                
                if force:
                    process.kill()
                else:
                    process.terminate()
                    
                self.controlled_processes[process_id]['status'] = 'killed'
                return True
            except Exception:
                return False
        return False
    
    def get_process_info(self, process_id: int) -> Optional[Dict[str, Any]]:
        """Информация о процессе"""
        if process_id in self.controlled_processes:
            proc_data = self.controlled_processes[process_id]
            process = proc_data['process']
            
            try:
                if psutil:
                    cpu_percent = psutil.Process(process.pid).cpu_percent()
                    memory_info = psutil.Process(process.pid).memory_info()
                else:
                    cpu_percent = 0
                    memory_info = None
            except:
                cpu_percent = 0
                memory_info = None
                
            return {
                'pid': process.pid,
                'command': proc_data['command'],
                'status': proc_data['status'],
                'created_at': proc_data['created_at'],
                'cpu_percent': cpu_percent,
                'memory_rss': memory_info.rss if memory_info else 0,
                'memory_vms': memory_info.vms if memory_info else 0
            }
        return None

class BloodCCompiler:
    """
    C компилятор для выполнения C скриптов в трансформерах Nicole
    Использует компоненты Clang из nicole2c
    """
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "nicole_blood"
        self.temp_dir.mkdir(exist_ok=True)
        self.compiled_cache = {}
        
    def compile_c_code(self, c_code: str, function_name: str = "main") -> Optional[str]:
        """
        Компилирует C код и возвращает путь к исполняемому файлу
        Для использования в трансформерах Nicole
        """
        # Создаем хеш для кеширования
        code_hash = hash(c_code)
        
        if code_hash in self.compiled_cache:
            return self.compiled_cache[code_hash]
        
        try:
            # Создаем временные файлы
            c_file = self.temp_dir / f"blood_{code_hash}.c"
            exe_file = self.temp_dir / f"blood_{code_hash}"
            
            # Записываем C код
            with open(c_file, 'w') as f:
                f.write(c_code)
            
            # Компилируем с помощью системного GCC (пока без Clang)
            # TODO: Интегрировать компоненты Clang из nicole2c
            compile_cmd = [
                'gcc',
                '-O2',
                '-o', str(exe_file),
                str(c_file)
            ]
            
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.compiled_cache[code_hash] = str(exe_file)
                return str(exe_file)
            else:
                raise RuntimeError(f"Compilation failed: {result.stderr}")
                
        except Exception as e:
            raise RuntimeError(f"Blood C compilation error: {e}")
    
    def execute_c_script(self, c_code: str, args: List[str] = None, timeout: int = 10) -> Dict[str, Any]:
        """
        Компилирует и выполняет C скрипт
        Возвращает результат выполнения
        """
        exe_path = self.compile_c_code(c_code)
        
        if not exe_path:
            return {'success': False, 'error': 'Compilation failed'}
        
        try:
            cmd = [exe_path] + (args or [])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': True,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': timeout
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Execution timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class BloodSystemInterface:
    """
    Системный интерфейс для низкоуровневого контроля
    Nicole использует это для прямого взаимодействия с ОС
    """
    
    def __init__(self):
        self.signal_handlers = {}
        
    def set_signal_handler(self, sig: int, handler):
        """Установка обработчика сигнала"""
        self.signal_handlers[sig] = handler
        signal.signal(sig, handler)
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Получение информации о системных ресурсах"""
        try:
            result = {
                'cpu_count': os.cpu_count(),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
            if psutil:
                result.update({
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory': dict(psutil.virtual_memory()._asdict()),
                    'disk': dict(psutil.disk_usage('/')._asdict()),
                    'boot_time': psutil.boot_time()
                })
            else:
                result.update({
                    'cpu_percent': 0,
                    'memory': {'available': 0, 'total': 0},
                    'disk': {'free': 0, 'total': 0},
                    'boot_time': 0
                })
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def direct_syscall(self, syscall_name: str, *args) -> Any:
        """
        Прямой системный вызов (осторожно!)
        Для критических операций в трансформерах
        """
        # Пока заглушка - требует осторожной реализации
        return f"SYSCALL {syscall_name} with args {args} - NOT IMPLEMENTED"

class BloodCore:
    """
    Ядро Blood системы - главный интерфейс для Nicole
    Объединяет все компоненты для контроля железа
    """
    
    def __init__(self):
        self.memory_manager = BloodMemoryManager()
        self.process_controller = BloodProcessController()
        self.c_compiler = BloodCCompiler()
        self.system_interface = BloodSystemInterface()
        
        self.is_active = False
        self.log_file = "blood_system.log"
        
    def activate(self) -> bool:
        """Активация Blood системы"""
        try:
            self.is_active = True
            self._log_info("Blood system activated - Nicole has iron control")
            return True
        except Exception as e:
            self._log_error(f"Blood activation failed: {e}")
            return False
    
    def deactivate(self):
        """Blood system deactivation"""
        # Clear memory blocks
        for addr in list(self.memory_manager.allocated_blocks.keys()):
            self.memory_manager.deallocate_raw(addr)
        
        # Terminate processes
        for proc_id in list(self.process_controller.controlled_processes.keys()):
            self.process_controller.kill_process(proc_id, force=True)
        
        self.is_active = False
        self._log_info("Blood system deactivated")
    
    def execute_transformer_c_script(self, transformer_id: str, c_code: str) -> Dict[str, Any]:
        """
        Execute C script in Nicole transformer context
        Key function for transformer integration
        """
        if not self.is_active:
            return {'success': False, 'error': 'Blood system not active'}
        
        self._log_info(f"Executing C script for transformer {transformer_id}")
        
        try:
            result = self.c_compiler.execute_c_script(c_code)
            
            # Добавляем контекст трансформера
            result['transformer_id'] = transformer_id
            result['execution_timestamp'] = time.time()
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'transformer_id': transformer_id
            }
    
    def get_full_system_status(self) -> Dict[str, Any]:
        """Полный статус Blood системы"""
        return {
            'active': self.is_active,
            'memory': self.memory_manager.get_memory_stats(),
            'processes': len(self.process_controller.controlled_processes),
            'system_resources': self.system_interface.get_system_resources(),
            'compiler_cache_size': len(self.c_compiler.compiled_cache)
        }
    
    def _log_info(self, message: str):
        """Логирование для системы"""
        with open(self.log_file, "a") as f:
            f.write(f"[BLOOD:INFO] {time.time()}: {message}\n")
    
    def _log_error(self, message: str):
        """Логирование ошибок"""
        with open(self.log_file, "a") as f:
            f.write(f"[BLOOD:ERROR] {time.time()}: {message}\n")

# Глобальный экземпляр Blood системы
_blood_core = None

def get_blood_core() -> BloodCore:
    """Получение глобального экземпляра Blood системы"""
    global _blood_core
    if _blood_core is None:
        _blood_core = BloodCore()
    return _blood_core

def activate_blood_system() -> bool:
    """Активация Blood системы для Nicole"""
    blood = get_blood_core()
    return blood.activate()

def deactivate_blood_system():
    """Деактивация Blood системы"""
    blood = get_blood_core()
    blood.deactivate()

# Пример использования C скрипта в трансформере
EXAMPLE_TRANSFORMER_C_SCRIPT = """
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main() {
    // Пример низкоуровневого контроля для трансформера Nicole
    printf("Nicole Transformer C Script Active\\n");
    printf("Process ID: %d\\n", getpid());
    printf("Memory allocation test...\\n");
    
    // Выделяем память
    void *ptr = malloc(1024 * 1024); // 1MB
    if (ptr) {
        printf("Memory allocated successfully\\n");
        free(ptr);
        printf("Memory freed\\n");
    }
    
    return 0;
}
"""

if __name__ == "__main__":
    # Тестирование Blood системы
    print("🩸 BLOOD SYSTEM - Nicole Iron Control")
    
    blood = get_blood_core()
    
    if blood.activate():
        print("✅ Blood system activated")
        
        # Тест системных ресурсов
        resources = blood.system_interface.get_system_resources()
        print(f"📊 System resources: CPU {resources.get('cpu_percent', 0)}%")
        
        # Тест C компиляции
        print("🔨 Testing C script compilation...")
        result = blood.execute_transformer_c_script("test_transformer", EXAMPLE_TRANSFORMER_C_SCRIPT)
        
        if result['success']:
            print("✅ C script executed successfully")
            print(f"Output: {result['stdout']}")
        else:
            print(f"❌ C script failed: {result['error']}")
        
        # Полный статус
        status = blood.get_full_system_status()
        print(f"🩸 Blood system status: {status}")
        
        blood.deactivate()
        print("✅ Blood system deactivated")
    else:
        print("❌ Blood system activation failed")
