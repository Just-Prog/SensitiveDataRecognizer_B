FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.5-slim-bullseye

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt -i https://mirrors.bfsu.edu.cn/pypi/web/simple/
# COPY bullseye.list /etc/apt/sources.list
RUN sed -i "s@http://\(deb\|security\).debian.org@https://mirrors.bfsu.edu.cn@g" /etc/apt/sources.list
RUN apt update
RUN apt install mime-support -y
RUN rm -fr /app/.git
RUN rm -fr /app/data
RUN rm -fr /app/flask_session
RUN mkdir /app/data
RUN mkdir /app/flask_session

ENV ENV=PROD

# ENV PG_SERVER=
# ENV PG_PORT= 
# ENV PG_USER= 
# ENV PG_PWD= 
# ENV PG_DB=

EXPOSE 5050
ENTRYPOINT ["python3", "run.py"]
