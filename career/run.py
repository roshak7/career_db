#!/usr/bin/env python
"""
Скрипт для запуска Career DB с поддержкой Python 3.7 и 3.12
"""
import os
import sys
import warnings
import platform

def check_python_version():
    """Проверяет версию Python и выводит информацию"""
    version = sys.version_info
    print(f"Текущая версия Python: {platform.python_version()}")
    if version.major == 3 and (version.minor == 7 or version.minor == 12):
        print("Поддерживаемая версия Python")
    else:
        warnings.warn(f"Python {version.major}.{version.minor} может не полностью поддерживаться. Рекомендуемые версии: 3.7 или 3.12")

def setup_environment():
    """Настраивает переменные окружения для запуска проекта"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings_base')
    
    # Отключаем предупреждения о устаревших функциях
    # Это важно для совместимости с Python 3.12
    warnings.filterwarnings("ignore", category=DeprecationWarning)

def run_server(port=8000):
    """Запускает сервер Django на указанном порту"""
    from django.core.management import execute_from_command_line
    
    print(f"Запуск сервера на порту {port}...")
    execute_from_command_line([sys.argv[0], "runserver", f"127.0.0.1:{port}"])

def main():
    """Основная функция для запуска проекта"""
    check_python_version()
    setup_environment()
    
    try:
        if len(sys.argv) > 1:
            # Если переданы аргументы, передаем их в Django
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
        else:
            # По умолчанию запускаем сервер
            port = 8000
            run_server(port)
    except Exception as e:
        print(f"Ошибка при запуске проекта: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 