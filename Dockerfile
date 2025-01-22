FROM python:3.12

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./votx /code/votx

CMD ["uvicorn", "votx.main:app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "8008"]
