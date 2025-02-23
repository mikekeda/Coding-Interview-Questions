from celery import Celery
from celery.schedules import crontab

app = Celery("api")
app.config_from_object("api.settings", namespace="CELERY")

app.autodiscover_tasks(["api"])

app.conf.beat_schedule = {
    "every-hour": {
        "task": "api.tasks.cget_new_problems",
        "schedule": crontab(hour="8", minute="15"),
        "args": (),
    },
}
