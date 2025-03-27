#!/usr/bin/env python
"""
Скрипт для настройки проекта Career DB
Создает виртуальные окружения для Python 3.7 и 3.12 и устанавливает зависимости
"""
import os
import sys
import subprocess
import platform

def get_python_path(version):
    """Получает путь к Python указанной версии"""
    if platform.system() == "Windows":
        # На Windows проверяем доступность Python через команду 'py'
        try:
            result = subprocess.run(f"py -{version} --version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"py -{version}"
        except:
            pass
    
    # Проверяем наличие python с указанной версией
    python_cmd = f"python{version}"
    try:
        result = subprocess.run(f"{python_cmd} --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return python_cmd
    except:
        pass
    
    # Проверяем просто 'python'
    try:
        result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and f"Python 3.{version}" in result.stdout:
            return "python"
    except:
        pass
    
    return None

def create_venv(python_path, venv_name):
    """Создает виртуальное окружение с указанным именем"""
    print(f"Создание виртуального окружения {venv_name}...")
    subprocess.run(f"{python_path} -m venv {venv_name}", shell=True, check=True)
    print(f"Виртуальное окружение {venv_name} создано успешно")

def install_requirements(venv_name):
    """Устанавливает зависимости в виртуальное окружение"""
    print(f"Установка зависимостей в {venv_name}...")
    
    # Определяем команду активации в зависимости от ОС
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\\Scripts\\activate.bat"
        pip_cmd = f"{venv_name}\\Scripts\\pip"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        pip_cmd = f"{venv_name}/bin/pip"
    
    # Обновляем pip
    subprocess.run(f"{pip_cmd} install --upgrade pip", shell=True, check=True)
    
    # Устанавливаем зависимости
    subprocess.run(f"{pip_cmd} install -r requirements.txt", shell=True, check=True)
    
    print(f"Зависимости установлены в {venv_name}")

def main():
    """Основная функция скрипта"""
    print("Настройка проекта Career DB...")
    
    # Проверяем наличие Python 3.7
    python37 = get_python_path("3.7")
    if python37:
        print(f"Python 3.7 найден: {python37}")
        try:
            create_venv(python37, "venv37")
            install_requirements("venv37")
        except Exception as e:
            print(f"Ошибка при настройке Python 3.7: {e}")
    else:
        print("Python 3.7 не найден на вашей системе")
    
    # Проверяем наличие Python 3.12
    python312 = get_python_path("3.12")
    if python312:
        print(f"Python 3.12 найден: {python312}")
        try:
            create_venv(python312, "venv312")
            install_requirements("venv312")
        except Exception as e:
            print(f"Ошибка при настройке Python 3.12: {e}")
    else:
        print("Python 3.12 не найден на вашей системе")
    
    print("\nНастройка завершена.")
    print("Для активации виртуального окружения Python 3.7 используйте:")
    if platform.system() == "Windows":
        print("venv37\\Scripts\\activate.bat")
    else:
        print("source venv37/bin/activate")
    
    print("\nДля активации виртуального окружения Python 3.12 используйте:")
    if platform.system() == "Windows":
        print("venv312\\Scripts\\activate.bat")
    else:
        print("source venv312/bin/activate")
    
    print("\nПосле активации виртуального окружения, запустите проект командой:")
    print("python run.py")

if __name__ == "__main__":
    main() 