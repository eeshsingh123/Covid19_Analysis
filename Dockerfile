FROM ubuntu:18.04
RUN apt-get -q update
RUN apt-get -qy install tmux nginx curl gunicorn3 git
RUN apt-get update \
  && apt-get install -y python3-pip python3.7 libpq-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install pip==19.3.1

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN mkdir home/dashboard
RUN mkdir home/dashboard_data
WORKDIR home/dashboard
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
RUN chmod 755 /home/dashboard/auto_run.sh
ENTRYPOINT ["/home/dashboard/auto_run.sh"]
