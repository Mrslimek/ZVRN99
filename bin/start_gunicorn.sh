#!/bin/bash
exec uv run gunicorn -c 'path/to/your/gunicorn_config.py' config.wsgi
