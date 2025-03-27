@echo off
echo Запуск проекта Career DB...

:: Проверка активации виртуального окружения
if not defined VIRTUAL_ENV (
    echo Виртуальное окружение не активировано!
    echo Активируйте виртуальное окружение перед запуском сервера.
    echo Пример: venv312\Scripts\activate
    pause
    exit /b 1
)

:: Запуск скрипта проверки совместимости
python check_compatibility.py

:: Запуск сервера Django в фоновом режиме
start /b cmd /c "python run.py"

:: Небольшая задержка для запуска сервера
timeout /t 2 /nobreak > nul

:: Открытие браузера
echo Открытие браузера по адресу http://localhost:8000/
start http://localhost:8000/

echo Сервер запущен. Для доступа к веб-интерфейсу используйте:
echo - http://localhost:8000/app/ - фронтенд-приложение
echo - http://localhost:8000/admin/ - панель администратора
echo - http://localhost:8000/ - API документация
echo Для остановки нажмите Ctrl+C в окне сервера. 