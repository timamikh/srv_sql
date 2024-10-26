# Используем официальный образ Python версии 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все необходимые файлы приложения в рабочую директорию
COPY . /app

# Обновляем пакетное хранилище и устанавливаем MySQL клиент
RUN apt-get update && \
    apt-get install -y mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python (на основе файла requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["gunicorn", "-b", "127.0.0.1:8000", "srv_sql:app"]