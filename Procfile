web: gunicorn flaskr.app:app
worker: celery -A flaskr.services worker --loglevel=INFO
