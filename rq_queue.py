import sys
import redis
from rq import Worker, Queue, Connection
from config import REDIS_CONN, RQ_CHANNELS
from redis.exceptions import ConnectionError

conn = redis.Redis(**REDIS_CONN)

if __name__ == '__main__':
    listen = sys.argv[1:]

    if not listen:
        raise Exception("""No channel(listener) added. Ex. python3 -m rq_queue channel_name""")
    for i in listen:
        if i not in RQ_CHANNELS:
            raise Exception(f"channel `{i}` not registered in config. Allowed only {RQ_CHANNELS}")

    while 1:
        try:
            with Connection(conn):
                print(listen)
                worker = Worker(map(Queue, [RQ_CHANNELS[i] for i in listen]))
                worker.work()
        except ConnectionError:
            import time
            time.sleep(2)
            print("Waiting For redis connection")