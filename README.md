# Инструкция по установке проекта

## 1. Клонирование репозитория
```bash
git clone https://github.com/Mrslimek/ZVRN99.git
```

## 2. Переход в папку проекта
```bash
cd ZVRN99
```

## 3. Установка зависимостей через uv
```bash
uv sync
```

## 4. Создание `.env` файла с переменными окружения
Создайте файл `.env` в корневой папке проекта и добавьте в него следующие параметры, заменив значения на свои:

```
PG_USER = <ваш-пользователь>
PG_PASSWORD = <ваш-пароль>
PG_NAME = <имя-базы>
PG_HOST = "localhost" # Или название контейнера (сервиса, если через docker-compose), если бд в докере
PG_PORT = 5432
DJANGO_SECRET = "<секретный-ключ>"
DEBUG = False
```

## 5. Настройка `gunicorn_config.py`
В директории `config/` настройте `gunicorn_config.py`:

```
pythonpath = 'path/to/your/django/project' # Например: /home/www/projects/django_project
bind = '127.0.0.1:port' # Указываем здесь порт, который будет слушать gunicorn. Например 127.0.0.1:8000
# Указываем кол-во воркеров на основе кол-ва ядер хоста * 2 + 1. Например: 4 ядра у хоста - 9 воркеров
# Это не аксиома и зависит от нагрузки на сервере, есть задачи типа cpu bound, то стоит поставить кол-во воркеров
# равное кол-ву ядер в cpu вашего хоста
workers = 5
# Пользователь, от которого будет работать gunicorn.
# На сервере стоит создать пользователя, чтобы не запускать от рута
user = 'www'
# Максимальное кол-во заголовков на один запрос
limit_request_fields = 50
# Максимальная длина контента в заголовке. Тут - неограничено
limit_request_field_size = 0
# Переменная окружения для настроек django
raw_env = 'DJANGO_SETTINGS_MODULE=config.settings' 
```

## 6. Настройка `nginx`
В конфигурации nginx `/etc/nginx/nginx.conf` настройте следующее:
```
# Пользователя стоит использовать того же, от которого работает и gunicorn
# Стоит использовать пользователя, у которого ограниченные полномочия, не root
user <ваш-пользователь>; # Например: www
# Nginx сам будет адаптироваться под нагрузку
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

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
	ssl_prefer_server_ciphers on;

	access_log /var/log/nginx/access.log;

	gzip on;

    # Можно разкомментировать, если планируется использовать модульную настройку nginx,
    # Но здесь вся настройка в основном конфиге nginx.conf
	# include /etc/nginx/conf.d/*.conf;
	# include /etc/nginx/sites-enabled/*;

	server {
		listen <Внешний порт, который слушает nginx>; # Например, listen 80 для http или 443 для https
		server_name < Домен вашего сервиса >; # Например, server_name www.google.com

		location / {
			proxy_pass <URI адрес gunicorn>; # Например: proxy_pass http://127.0.0.1:5000
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		}

        # Адрес статики, по которому nginx будет отдавать статику
		location /static/ {
    		alias <Путь к STATIC_ROOT>; # Например: /home/www/projects/django_project/static
		}	
	}
}
```
После сохранения изменений конфига перезапустить nginx:
    `sudo nginx -t` # Проверка на наличие синтаксических ошибок и проблем со структурой
    `sudo service nginx restart` # Для systemd использовать systemctl

## 7. Запуск проекта
Удостовериться, что nginx работает (`sudo service nginx status`) # Для systemd использовать systemctl
Собрать статику в STATIC_ROOT:
    - `uv run manage.py collectstatic`
Запустить gunicorn:
    Запуск через скрипт:
    - `chmod +x ./bin/start_gunicorn.sh`
    - `./bin/start_gunicorn.sh`
    Запуск напрямую:
    - `uv run gunicorn --bind <адрес хоста>:<порт> --workers <кол-во воркеров> --log-level info --access-logfile access.log --error-logfile error.log config.wsgi`


