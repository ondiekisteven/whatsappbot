import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://h:pffa2ba6288eb64eebf2bff97dc93ef56f156dd8a2758163f96fb52b5db387a5f@ec2-54-235-172-120.compute-1.amazonaws.com:10199')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
