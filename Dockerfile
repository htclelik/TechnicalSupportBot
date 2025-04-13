# Используем официальный образ Python
FROM python:3.12-slim
LABEL authors="lelik.van-23"

# Устанавливаем рабочую директорию (лучше использовать /app)
WORKDIR /app

# Сначала копируем только requirements.txt для кэширования
COPY requirements.txt .



# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы проекта (включая папку app)
COPY . .
ENV PYTHONPATH=/app

# Команда запуска (указываем правильный путь к главному файлу)
CMD ["python", "app/main.py"]
