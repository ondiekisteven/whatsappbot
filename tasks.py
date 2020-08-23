import os
import celery
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()
app = celery.Celery("background messages")

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


@tl.job(interval=timedelta(seconds=10))
def job_every_minute():
    print("Hello, am being started every 10 seonds")


@app.task
def work():
    try:
        tl.start(block=True)
    except RuntimeError:
        pass
