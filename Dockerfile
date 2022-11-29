FROM python:3.9

WORKDIR /hide

COPY ./requirements.txt /hide/requirements.txt

RUN apt-get update && apt-get install -y cmake


RUN pip install --no-cache-dir --upgrade -r /hide/requirements.txt
RUN apt-get install -y ffmpeg

COPY . /hide/

COPY ./app /hide/app

WORKDIR /hide/app/api
RUN mkdir -p /temp

WORKDIR /hide
EXPOSE 80

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:9000","--workers", "4","--worker-class", "uvicorn.workers.UvicornWorker"]
