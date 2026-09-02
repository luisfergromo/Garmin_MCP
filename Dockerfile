FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Copiar archivos de configuración y README
COPY pyproject.toml README.md ./

# Copiar código fuente
COPY src/ ./src/
COPY telegram_bot.py .

# Instalar dependencias y paquete
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "telegram_bot.py"]
