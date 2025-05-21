#!/bin/bash
exec uv run gunicorn -c '/home/viktor/Documents/projects/test_task/gunicorn_config.py' config.wsgi
