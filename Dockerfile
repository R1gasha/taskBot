FROM python:3.10.6

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir app

RUN apt-get update

COPY req.txt /
RUN pip install --upgrade pip && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r req.txt

COPY ./src/aiogramBot.py /app
ENTRYPOINT ["python3", "/app/aiogramBot.py"]