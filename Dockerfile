FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apt-get update && apt-get install -y wait-for-it

COPY . .

EXPOSE 8000


CMD ["bash", "-c", "wait-for-it db:5432 -- alembic upgrade head -v && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
