import os
import celery
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()
app = celery.Celery("background messages")

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


@app.task
@tl.job(interval=timedelta(seconds=10))
def job_every_minute():
    print("job started")
