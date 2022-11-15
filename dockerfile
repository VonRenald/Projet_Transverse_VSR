FROM python:3
LABEL Maintainer="weisbrice@gmail.com"

WORKDIR /usr/app/src

COPY worker.py ./

EXPOSE 9090
EXPOSE 9080

CMD ["python3", "./worker.py"]