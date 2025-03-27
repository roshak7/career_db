# Career DB

Система для создания графиков и карт преемственности из Excel файлов.

## Особенности проекта

- Импорт данных из Excel файлов
- Построение интерактивных карт преемственности
- Визуализация организационной структуры
- Анализ кадрового потенциала

## Технические требования

Проект поддерживает Python версий 3.7 и 3.12. 

### Требования к системе

- Python 3.7 или 3.12
- PostgreSQL
- Виртуальное окружение Python (рекомендуется)

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <репозиторий>
cd career_db
```

### 2. Создание виртуального окружения

#### Для Python 3.7:
```bash
python -m venv venv37
source venv37/bin/activate  # На Linux/Mac
venv37\Scripts\activate     # На Windows
```

#### Для Python 3.12:
```bash
python -m venv venv312
source venv312/bin/activate  # На Linux/Mac
venv312\Scripts\activate     # На Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Измените параметры подключения к базе данных в файле `settings/settings_base.py`. По умолчанию используется PostgreSQL.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'career_bd',
        'USER': 'ваш_пользователь',
        'PASSWORD': 'ваш_пароль',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Миграции базы данных

```bash
python manage.py migrate
```

### 6. Создание администратора

```bash
python manage.py createsuperuser
```

## Запуск проекта

### Использование скриптов автозапуска

Для удобства в проекте есть скрипты, которые запускают сервер и автоматически открывают браузер:

#### Windows:
```bash
start_server.bat
```

#### Linux/Mac:
```bash
# Сначала нужно сделать скрипт исполняемым
chmod +x start_server.sh
./start_server.sh
```

### Стандартный запуск

```bash
python run.py
```

По умолчанию сервер запустится на порту 8000. После запуска вы можете открыть сайт по адресу:
- http://localhost:8000/ или 
- http://127.0.0.1:8000/

Не пытайтесь использовать 0.0.0.0:8000 напрямую в браузере, это адрес только для прослушивания сервером.

Вы можете изменить порт, указав его в командной строке:

```bash
python run.py runserver 8080
```

### Запуск с помощью manage.py

```bash
python manage.py runserver
```

## Доступные URL-адреса

После запуска проекта вам доступны следующие URL-адреса:

- **http://localhost:8000/** - API документация (Swagger)
- **http://localhost:8000/app/** - Фронтенд-приложение
- **http://localhost:8000/admin/** - Панель администратора Django
- **http://localhost:8000/api/v1/** - API версии 1
- **http://localhost:8000/api/v2/** - API версии 2

## Администрирование

Панель администратора доступна по адресу: http://localhost:8000/admin/

## Особенности работы с разными версиями Python

### Python 3.7

- Используются более старые версии библиотек pandas и numpy
- Полная совместимость с Django 2.2

### Python 3.12

- Используются современные версии библиотек
- Обеспечена обратная совместимость с Django 2.2

## Решение проблем

### JSONField

В проекте используется JSONField, который может иметь разные пути импорта в разных версиях Django. 
Это обрабатывается автоматически:

```python
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField
```

### Зависимости

Если у вас возникают проблемы с установкой зависимостей, попробуйте следующее:

```bash
pip install --upgrade pip
pip install -r requirements.txt --use-deprecated=legacy-resolver
```

## Решение проблем с часовым поясом

Если вы получаете ошибку `AssertionError: database connection isn't set to UTC`, это связано с настройками часового пояса в Django и PostgreSQL. Есть несколько способов решить эту проблему:

### Способ 1: Использовать SQLite (для тестирования)

По умолчанию проект настроен на использование SQLite для простоты тестирования. Это самый простой способ запустить проект без проблем с часовым поясом.

### Способ 2: Отключить USE_TZ в Django

В файле `settings/settings_base.py` уже установлено `USE_TZ = False`. Это отключает автоматическое преобразование часовых поясов Django и решает проблему.

### Способ 3: Настроить PostgreSQL

Если вы хотите использовать PostgreSQL, убедитесь, что ваша база данных настроена правильно:

1. Раскомментируйте настройки PostgreSQL в `settings/settings_base.py` и убедитесь, что там есть опция:
   ```python
   'OPTIONS': {
       'options': '-c timezone=UTC',
   },
   ```

2. Или выполните SQL-запрос для вашей базы данных:
   ```sql
   ALTER DATABASE career_bd SET timezone TO 'UTC';
   ```

### Проверка настроек

Вы можете запустить скрипт проверки для диагностики проблем:

```bash
python db_check.py
```

Этот скрипт проверит соединение с базой данных и настройки часового пояса.

Также можно использовать скрипт для проверки совместимости проекта с текущей версией Python:

```bash
python check_compatibility.py
``` 