import os
import celery
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()
app = celery.Celery("background messages")

REDIS_URL = 'redis://h:p19ab68194c2bd67b1f15134ed24d3a4fc0464585da96534f61f933ffb0007495@ec2-23-23-149-97.compute-1.amazonaws.com:27019'

app.conf.update(BROKER_URL=REDIS_URL,
                CELERY_RESULT_BACKEND=REDIS_URL)


@tl.job(interval=timedelta(seconds=10))
def job_every_minute():
    print("Hello, am being started every 10 seonds")


@app.task
def work():
    try:
        tl.start(block=True)
    except RuntimeError:
        pass
