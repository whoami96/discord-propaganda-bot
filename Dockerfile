# Wybór lekkiego obrazu bazowego
FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Zapobieganie buforowaniu logów Pythona (widoczne natychmiast w docker logs)
ENV PYTHONUNBUFFERED=1

# Kopiowanie plików zależności i instalacja
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie reszty plików aplikacji
COPY propaganda-bot.py .
COPY quotes.txt .

# Uruchomienie bota
CMD ["python", "propaganda-bot.py"]
