FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY frontend /app/frontend

CMD ["python", "app.py"]
