import os
import random
import time
import requests
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
QUOTES_FILE = "quotes.txt"
DAILY_DISPATCH_COUNT = 3

def load_quotes():
    """Loads quotes from the external text file."""
    if not os.path.exists(QUOTES_FILE):
        print(f"BŁĄD: Plik {QUOTES_FILE} nie istnieje.")
        return []
    
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes

def generate_schedule(count=3):
    """Generates random timestamps within the current day."""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = []
    for _ in range(count):
        random_seconds = random.randint(0, 86400)
        timestamps.append(start_of_day + timedelta(seconds=random_seconds))

    return sorted(timestamps)

def send_to_discord(quote):
    """Sends a formatted message using the Discord Webhook."""
    payload = {
        "content": f"### 📜 **Historyczny Easter Egg**\n\n> {quote}"
    }
    try:
        # WEBHOOK_URL is guaranteed to exist here due to check in main()
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wiadomość wysłana pomyślnie.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Błąd Webhooka: status {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Problem z połączeniem: {e}")

def main():
    # Strict check for the Webhook URL
    if not WEBHOOK_URL:
        print("CRITICAL ERROR: Nie znaleziono zmiennej DISCORD_WEBHOOK_URL!")
        print("Upewnij się, że masz plik .env z wpisem: DISCORD_WEBHOOK_URL=twój_url")
        print("Lub ustaw zmienną w systemie: export DISCORD_WEBHOOK_URL='twój_url'")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Inicjalizacja bota...")
    
    quotes = load_quotes()
    if not quotes:
        print("CRITICAL ERROR: Brak cytatów do wysyłki. Zamykanie.")
        sys.exit(1)

    last_reset_date = None
    schedule = []

    while True:
        now = datetime.now()
        current_date = now.date()

        if last_reset_date != current_date:
            schedule = generate_schedule(DAILY_DISPATCH_COUNT)
            last_reset_date = current_date
            print(f"--- Nowy dzień: {current_date} ---")
            print(f"Harmonogram: {[t.strftime('%H:%M:%S') for t in schedule]}")

        for scheduled_time in schedule[:]:
            if now >= scheduled_time:
                selected_quote = random.choice(quotes)
                print(f"[{now.strftime('%H:%M:%S')}] Wysyłka dla zaplanowanej godziny {scheduled_time.strftime('%H:%M:%S')}")
                send_to_discord(selected_quote)
                schedule.remove(scheduled_time)
        
        time.sleep(30)

if __name__ == "__main__":
    main()
