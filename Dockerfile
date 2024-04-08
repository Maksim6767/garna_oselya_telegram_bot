# Используем базовый образ Python
FROM python:3.8

# Устанавливаем переменную окружения для предотвращения вывода сообщений об интерактивной установке
ENV DEBIAN_FRONTEND=noninteractive

# Обновляем пакеты и устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем директорию приложения в контейнере
WORKDIR /app

# Копируем зависимости проекта и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из текущей директории в контейнер
COPY . .

# Команда для запуска вашего бота
CMD ["python", "bot.py"]