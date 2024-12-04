from celery import Celery

from celery_config import get_celery_config

settings = get_celery_config()

celery_app = Celery()
celery_app.conf.update(settings.get_celery_config())
celery_app.autodiscover_tasks(["scrapers"], force=True)
