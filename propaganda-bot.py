import argparse
import os
import random
import sys
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
QUOTES_FILE = "quotes.txt"
# Load daily dispatch count from environment variable, default to 3
try:
    DAILY_DISPATCH_COUNT = int(os.getenv("DAILY_DISPATCH_COUNT", "3"))
except ValueError:
    print("WARNING: Invalid DAILY_DISPATCH_COUNT in .env. Defaulting to 3.")
    DAILY_DISPATCH_COUNT = 3


def load_quotes():
    """Loads quotes from the external text file."""
    if not os.path.exists(QUOTES_FILE):
        print(f"ERROR: File {QUOTES_FILE} does not exist.")
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


def send_to_discord(quote, remaining_today=0):
    """Sends a rich Embed message using the Discord Webhook."""
    
    # Discord Embed structure
    payload = {
        "embeds": [
            {
                "title": "📢 Historical Propaganda Moment",
                "description": f"### *\"{quote}\"*",
                "color": 15158332,  # Vivid Red
                "footer": {
                    "text": f"Historical Archive Bot • Quotes remaining today: {remaining_today}"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Message sent successfully.")
        else:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Webhook Error: status {response.status_code}"
            )
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connection problem: {e}")


def main():
    parser = argparse.ArgumentParser(description="Discord Propaganda Bot")
    parser.add_argument(
        "--now", action="store_true", help="Send a quote immediately and exit"
    )
    args = parser.parse_args()

    # Strict check for the Webhook URL
    if not WEBHOOK_URL:
        print("CRITICAL ERROR: DISCORD_WEBHOOK_URL environment variable not found!")
        print("Ensure you have a .env file with: DISCORD_WEBHOOK_URL=your_url")
        sys.exit(1)

    quotes = load_quotes()
    if not quotes:
        print("CRITICAL ERROR: No quotes to send. Shutting down.")
        sys.exit(1)

    if args.now:
        selected_quote = random.choice(quotes)
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Manual trigger: sending quote now..."
        )
        send_to_discord(selected_quote, remaining_today="N/A (Manual Trigger)")
        sys.exit(0)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initializing bot...")
    print(f"Configured daily dispatch count: {DAILY_DISPATCH_COUNT}")

    last_reset_date = None
    schedule = []

    while True:
        now = datetime.now()
        current_date = now.date()

        if last_reset_date != current_date:
            schedule = generate_schedule(DAILY_DISPATCH_COUNT)
            last_reset_date = current_date
            print(f"--- New Day: {current_date} ---")
            print(f"Schedule: {[t.strftime('%H:%M:%S') for t in schedule]}")

        for scheduled_time in schedule[:]:
            if now >= scheduled_time:
                selected_quote = random.choice(quotes)
                schedule.remove(scheduled_time)
                print(
                    f"[{now.strftime('%H:%M:%S')}] Sending for scheduled time {scheduled_time.strftime('%H:%M:%S')}"
                )
                send_to_discord(selected_quote, remaining_today=len(schedule))

        time.sleep(30)


if __name__ == "__main__":
    main()
