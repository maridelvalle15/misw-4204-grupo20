web: gunicorn flaskr.app:app --timeout 180
worker: celery -A flaskr.services worker --loglevel=INFO
