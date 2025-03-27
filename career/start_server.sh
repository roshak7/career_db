#!/bin/bash

echo "Запуск проекта Career DB..."

# Проверка активации виртуального окружения
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Виртуальное окружение не активировано!"
    echo "Активируйте виртуальное окружение перед запуском сервера."
    echo "Пример: source venv312/bin/activate"
    exit 1
fi

# Запуск скрипта проверки совместимости
python check_compatibility.py

# Запуск сервера Django в фоновом режиме
python run.py &
SERVER_PID=$!

# Небольшая задержка для запуска сервера
sleep 2

# Открытие браузера (работает на разных системах)
if [ "$(uname)" == "Darwin" ]; then
    # Mac OS X
    open http://localhost:8000/
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:8000/
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:8000/
    else
        echo "Откройте браузер и перейдите по адресу: http://localhost:8000/"
    fi
fi

echo "Сервер запущен. Для остановки нажмите Ctrl+C"
echo "PID сервера: $SERVER_PID"
echo "Для доступа к веб-интерфейсу используйте:"
echo "- http://localhost:8000/app/ - фронтенд-приложение"
echo "- http://localhost:8000/admin/ - панель администратора"
echo "- http://localhost:8000/ - API документация"

# Ожидание сигнала для корректного завершения
trap "kill $SERVER_PID; exit" INT TERM
wait $SERVER_PID 