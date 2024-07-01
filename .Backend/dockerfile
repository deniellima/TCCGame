
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY Backend/ .

EXPOSE 5000

CMD ["waitress-serve", "--port=5000", "--call", "app:create_app"]
