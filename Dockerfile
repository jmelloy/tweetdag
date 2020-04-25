FROM python:2.7-slim
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code

RUN pip install -r requirements.txt

COPY . /code

ENTRYPOINT [ "/code/tweetdag.py" ]
