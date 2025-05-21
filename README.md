# Инструкция по установке проекта

## 1. Клонирование репозитория
Клонируйте проект с GitHub:

```bash
git clone https://github.com/Mrslimek/ZVRN99.git
```

## 2. Переход в папку проекта
Перейдите в директорию проекта:

```bash
cd ZVRN99
```

## 3. Установка зависимостей через uv
Установите зависимости:

```bash
uv sync
```

---

## 4. Создание `.env` файла с переменными окружения
Создайте файл `.env` в корневой папке проекта и добавьте в него следующие параметры, заменив значения на свои:

```env
PG_USER = <ваш-пользователь>
PG_PASSWORD = <ваш-пароль>
PG_NAME = <имя-базы>
PG_HOST = "localhost"  # Или название контейнера (сервиса, если БД в Docker)
PG_PORT = 5432
DJANGO_SECRET = "<секретный-ключ>"
DEBUG = False
```

---

## 5. Настройка `gunicorn_config.py`
В директории `config/` настройте `gunicorn_config.py`:

```python
pythonpath = 'path/to/your/django/project'  # Например: /home/www/projects/django_project
bind = '127.0.0.1:<порт>'  # Указываем порт, который будет слушать Gunicorn, например 127.0.0.1:8000

# Указываем количество воркеров на основе числа ядер хоста * 2 + 1. Например:
# 4 ядра у хоста → 9 воркеров
# Это не аксиома и зависит от нагрузки. Если задачи CPU-bound, лучше установить количество воркеров 
# равное количеству ядер CPU вашего хоста.
workers = 5

# Пользователь, от которого будет работать Gunicorn.
# На сервере стоит создать отдельного пользователя, чтобы не запускать от root.
user = 'www'

# Ограничения на заголовки запросов
limit_request_fields = 50  # Максимальное количество заголовков на один запрос
limit_request_field_size = 0  # Максимальная длина контента в заголовке (0 = без ограничений)

# Переменная окружения для настроек Django
raw_env = 'DJANGO_SETTINGS_MODULE=config.settings'
```

---

## 6. Настройка `nginx`
В конфигурации Nginx `/etc/nginx/nginx.conf` настройте следующее:

```nginx
# Пользователь должен совпадать с тем, от имени которого работает Gunicorn
user <ваш-пользователь>;  # Например: www

# Nginx автоматически адаптируется под нагрузку
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1.2 TLSv1.3;  # Dropping old SSL versions
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;

    gzip on;

    # Можно разкомментировать, если планируется использовать модульную настройку Nginx,
    # Но здесь вся настройка в основном конфиге nginx.conf
    # include /etc/nginx/conf.d/*.conf;
    # include /etc/nginx/sites-enabled/*;

    server {
        listen <Внешний порт, который слушает Nginx>;  # Например, listen 80 для HTTP или 443 для HTTPS
        server_name <Домен вашего сервиса>;  # Например, server_name www.google.com;

        location / {
            proxy_pass <URI Gunicorn>;  # Например: proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Адрес статики, по которому Nginx будет отдавать файлы
        location /static/ {
            alias <Путь к STATIC_ROOT>;  # Например: /home/www/projects/django_project/static;
        }
    }
}
```

### Перезапуск Nginx после изменений:
```bash
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx  # Перезапуск (или `sudo service nginx restart` для старых систем)
```

---

## 7. Запуск проекта

### Проверка, что Nginx работает:
```bash
sudo systemctl status nginx  # Проверка состояния службы
```

### Сбор статики Django:
```bash
uv run manage.py collectstatic
```

### Запуск Gunicorn:
#### Через скрипт:
```bash
chmod +x ./bin/start_gunicorn.sh
./bin/start_gunicorn.sh
```

#### Напрямую:
```bash
uv run gunicorn --bind <адрес хоста>:<порт> --workers <кол-во воркеров> --log-level info --access-logfile access.log --error-logfile error.log config.wsgi
```

```Готово! Можно проверять```