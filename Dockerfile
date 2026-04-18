FROM python:3.11-alpine3.20

RUN apk update && apk upgrade --no-cache

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

RUN chown -R appuser:appgroup /usr/src/app

USER appuser

EXPOSE 8080

CMD ["python", "app/main.py"]
