#!/usr/bin/env python
"""
Скрипт для проверки совместимости с Python 3.7 и 3.12
"""
import sys
import platform
import os
import importlib.util
import warnings

def check_python_version():
    """Проверяет версию Python и совместимость"""
    version = sys.version_info
    print(f"Текущая версия Python: {platform.python_version()}")
    
    if version.major == 3:
        if version.minor == 7:
            print("Python 3.7 - полностью поддерживается.")
            compatible = True
        elif version.minor == 12:
            print("Python 3.12 - поддерживается с учетом обновленных зависимостей.")
            compatible = True
        else:
            print(f"Python 3.{version.minor} - может быть частично совместим.")
            compatible = False
    else:
        print(f"Python {version.major}.{version.minor} - не проверено на совместимость.")
        compatible = False
    
    return compatible

def check_package_compatibility():
    """Проверяет совместимость основных пакетов"""
    packages_to_check = [
        "django",
        "pandas",
        "numpy",
        "matplotlib",
        "psycopg2",
        "pygame",
        "openpyxl",
        "pillow"
    ]
    
    print("\nПроверка установленных пакетов:")
    
    results = []
    for package in packages_to_check:
        spec = importlib.util.find_spec(package)
        if spec is None:
            status = "не найден"
            version = "отсутствует"
            results.append((package, status, version, False))
        else:
            try:
                module = importlib.import_module(package)
                version = getattr(module, "__version__", "неизвестно")
                status = "установлен"
                results.append((package, status, version, True))
            except Exception as e:
                status = "ошибка импорта"
                version = str(e)
                results.append((package, status, version, False))
    
    for package, status, version, is_available in results:
        if is_available:
            print(f"✓ {package}: {status} (версия {version})")
        else:
            print(f"✗ {package}: {status}")
    
    missing_packages = [p[0] for p in results if not p[3]]
    if missing_packages:
        print(f"\nОтсутствуют необходимые пакеты: {', '.join(missing_packages)}")
        print("Рекомендуется установить их с помощью pip:")
        print(f"pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_django_settings():
    """Проверяет настройки Django для совместимости"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings_base')
        import django
        django.setup()
        
        from django.conf import settings
        
        print("\nПроверка настроек Django:")
        
        # Проверяем настройки часового пояса
        if hasattr(settings, 'USE_TZ') and settings.USE_TZ:
            print("✗ USE_TZ=True - может вызвать проблемы с базой данных.")
            print("  Рекомендуется установить USE_TZ=False в settings_base.py")
        else:
            print("✓ USE_TZ=False - правильная настройка для этого проекта.")
        
        # Проверяем настройки базы данных
        if hasattr(settings, 'DATABASES'):
            engine = settings.DATABASES['default']['ENGINE']
            print(f"База данных: {engine}")
            
            if 'sqlite3' in engine:
                print("✓ SQLite - хорошо подходит для тестирования.")
            elif 'postgresql' in engine:
                print("✓ PostgreSQL - основная база данных проекта.")
                
                # Проверяем настройки часового пояса для PostgreSQL
                if 'OPTIONS' in settings.DATABASES['default'] and 'options' in settings.DATABASES['default']['OPTIONS']:
                    if '-c timezone=UTC' in settings.DATABASES['default']['OPTIONS']['options']:
                        print("✓ Настройки часового пояса PostgreSQL установлены правильно.")
                    else:
                        print("✗ Настройки часового пояса PostgreSQL могут быть неправильными.")
                else:
                    print("✗ Отсутствуют OPTIONS для PostgreSQL с настройкой часового пояса.")
                    print("  Добавьте 'OPTIONS': {'options': '-c timezone=UTC'} в настройки DATABASES.")
    except Exception as e:
        print(f"\nОшибка при проверке настроек Django: {e}")
        return False
    
    return True

def main():
    """Основная функция проверки совместимости"""
    print("=== Проверка совместимости проекта ===\n")
    
    # Проверяем версию Python
    python_compatible = check_python_version()
    
    # Проверяем установленные пакеты
    packages_compatible = check_package_compatibility()
    
    # Проверяем настройки Django
    django_compatible = check_django_settings()
    
    # Выводим итоговый результат
    print("\n=== Итоговый результат ===\n")
    
    if python_compatible and packages_compatible and django_compatible:
        print("✓ Проект совместим с текущей версией Python и установленными пакетами.")
        print("  Можно запустить проект с помощью команды: python run.py")
    else:
        print("✗ Обнаружены проблемы совместимости.")
        print("  Пожалуйста, устраните указанные выше проблемы.")
    
    print("\nДля изменения базы данных на PostgreSQL или SQLite, отредактируйте файл settings_base.py.")

if __name__ == "__main__":
    main() 