from redis import Redis
from rq_scheduler import Scheduler

from config import REDIS_CONN

RCONN = Redis(**REDIS_CONN)


def kill_schedule(channel, verbose=True):
    try:
        scheduler = Scheduler(channel, connection=RCONN)
        jobs_and_times = scheduler.get_jobs(with_times=True)
        for job in jobs_and_times:
            print("job", job)
            scheduler.cancel(job[0].id)
        if verbose:
            print("All Jobs Killed")
        return True
    except Exception as e:
        print("Errors in killing jobs", e)
        return False


if __name__ == "__main__":
    pass