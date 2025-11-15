FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install aiogram==3.4

CMD ["python3", "bot.py"]
