from rq import Queue
from worker import conn
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()


@tl.job(interval=timedelta(seconds=10))
def job_every_minute():
    print("job started")


q = Queue(connection=conn)

q.enqueue(tl.start(block=True))
