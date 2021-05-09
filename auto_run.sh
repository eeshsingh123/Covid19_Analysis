#!/bin/sh

export INTERNAL_HOST_IP=$(ip route show default | awk '/default/ {print $3}')

/usr/bin/tmux new-session -d -s rq_queue_data_updater \; send-keys "cd /home/dashboard/ && python3 -m rq_queue data_updater" Enter
/usr/bin/tmux new-session -d -s rq_scheduler \; send-keys "rqscheduler -v --host localhost --port 6379" Enter

/usr/bin/tmux new-session -d -s app_twitter_main \; send-keys "python3 -m app.twitter_main" Enter

/usr/bin/gunicorn3 --chdir /home/dashboard/ --timeout 1000 wsgi:app -b 0.0.0.0:7916