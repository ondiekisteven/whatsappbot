import logging
import os

import redis
import riprova
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

logger = logging.getLogger(__name__)


def on_retry(err, next_try):
    logger.warning('Operation error: {}'.format(err))
    logger.warning('Next try in: {}ms'.format(next_try))


@riprova.retry(backoff=riprova.ExponentialBackOff(factor=0.5), on_retry=on_retry)
def main():
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


if __name__ == '__main__':
    main()
