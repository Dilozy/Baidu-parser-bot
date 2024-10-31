FROM python:3

# Копируем код приложения
COPY . /app
# Устанавливаем рабочую директорию
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Команда для выполнения вашего кода
CMD ["python", "bot.py"]
