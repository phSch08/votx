FROM python:3.12

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./votx /code/votx

CMD ["fastapi", "run", "votx/main.py", "--proxy-headers", "--port", "8008"]