import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_mooli_project.settings')
app = Celery('the_mooli_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()