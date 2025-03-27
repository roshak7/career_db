#!/usr/bin/env python
"""
Скрипт для проверки соединения с базой данных и исправления проблем с часовым поясом
"""
import os
import sys
import django
import warnings

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings_base')

# Инициализируем Django
django.setup()

# Импортируем необходимые модули
from django.db import connection
from django.conf import settings

def check_database_connection():
    """Проверяет соединение с базой данных"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Соединение с базой данных успешно установлено: {result}")
            return True
    except Exception as e:
        print(f"Ошибка при соединении с базой данных: {e}")
        return False

def check_timezone_settings():
    """Проверяет настройки часового пояса в Django и базе данных"""
    print(f"Настройки часового пояса в Django:")
    print(f"TIME_ZONE = {settings.TIME_ZONE}")
    print(f"USE_TZ = {settings.USE_TZ}")
    
    try:
        with connection.cursor() as cursor:
            # Проверяем настройки часового пояса в PostgreSQL
            cursor.execute("SHOW timezone;")
            db_timezone = cursor.fetchone()[0]
            print(f"\nНастройки часового пояса в базе данных:")
            print(f"Текущий часовой пояс PostgreSQL: {db_timezone}")
            
            # Проверяем, можем ли мы изменить часовой пояс для текущей сессии
            try:
                cursor.execute("SET TIME ZONE 'UTC';")
                cursor.execute("SHOW timezone;")
                new_timezone = cursor.fetchone()[0]
                print(f"Часовой пояс сессии изменен на: {new_timezone}")
            except Exception as e:
                print(f"Не удалось изменить часовой пояс сессии: {e}")
    except Exception as e:
        print(f"Ошибка при проверке настроек часового пояса: {e}")

def fix_timezone_issue():
    """Пытается исправить проблему с часовым поясом"""
    print("Попытка исправления проблемы с часовым поясом...")
    
    # Проверяем, установлено ли USE_TZ в False
    if settings.USE_TZ:
        print("Настройка USE_TZ=True. Рекомендуется изменить на USE_TZ=False в settings_base.py")
    else:
        print("Настройка USE_TZ=False. Это должно решить проблему с часовым поясом.")
    
    try:
        # Создаем новое соединение с настройкой часового пояса
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Тестовый запрос с установкой часового пояса UTC выполнен успешно: {result}")
            
            # Проверяем, сохраняется ли настройка часового пояса
            cursor.execute("SHOW timezone;")
            timezone = cursor.fetchone()[0]
            print(f"Текущий часовой пояс сессии: {timezone}")
            
            if timezone == 'UTC':
                print("Часовой пояс сессии успешно установлен в UTC.")
            else:
                print(f"Предупреждение: часовой пояс сессии ({timezone}) отличается от UTC.")
    except Exception as e:
        print(f"Ошибка при исправлении проблемы с часовым поясом: {e}")

def main():
    """Основная функция проверки базы данных"""
    print("=== Проверка базы данных ===\n")
    
    # Проверяем соединение с базой данных
    if not check_database_connection():
        print("\nПроверьте настройки подключения к базе данных в settings_base.py.")
        sys.exit(1)
    
    print("\n=== Проверка настроек часового пояса ===\n")
    
    # Проверяем настройки часового пояса
    check_timezone_settings()
    
    print("\n=== Попытка исправления проблемы с часовым поясом ===\n")
    
    # Пытаемся исправить проблему с часовым поясом
    fix_timezone_issue()
    
    print("\n=== Рекомендации ===\n")
    
    print("1. Установите USE_TZ = False в settings_base.py, если это еще не сделано.")
    print("2. Убедитесь, что PostgreSQL правильно настроен.")
    print("3. Если проблема не решена, попробуйте выполнить в PostgreSQL:")
    print("   ALTER DATABASE career_bd SET timezone TO 'UTC';")
    print("   (Замените 'career_bd' на имя вашей базы данных)")

if __name__ == "__main__":
    main() 