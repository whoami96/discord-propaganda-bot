import argparse
import os
import random
import sys
import time
from datetime import UTC, datetime, timedelta

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

# Quiet Hours configuration
try:
    QUIET_HOURS_START = int(os.getenv("QUIET_HOURS_START", "23"))
    QUIET_HOURS_END = int(os.getenv("QUIET_HOURS_END", "8"))
except ValueError:
    print("WARNING: Invalid QUIET_HOURS configuration in .env. Defaulting to 23-8.")
    QUIET_HOURS_START = 23
    QUIET_HOURS_END = 8


def is_quiet_hour(hour, start, end):
    """Checks if the given hour falls within the quiet hours range."""
    if start < end:
        return start <= hour < end
    else:  # Range crosses midnight (e.g., 23 to 8)
        return hour >= start or hour < end


def load_quotes():
    """Loads quotes from the external text file."""
    if not os.path.exists(QUOTES_FILE):
        print(f"ERROR: File {QUOTES_FILE} does not exist.")
        return []

    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes


def generate_schedule(count=3):
    """Generates random timestamps within the current day, respecting quiet hours."""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = []
    attempts = 0
    max_attempts = count * 100  # Safety break

    while len(timestamps) < count and attempts < max_attempts:
        random_seconds = random.randint(0, 86400 - 1)
        candidate_time = start_of_day + timedelta(seconds=random_seconds)

        if not is_quiet_hour(candidate_time.hour, QUIET_HOURS_START, QUIET_HOURS_END):
            timestamps.append(candidate_time)
        attempts += 1

    return sorted(timestamps)


def send_to_discord(quote, remaining_today=0):
    """Sends a rich Embed message using the Discord Webhook."""

    # Discord Embed structure
    payload = {
        "embeds": [
            {
                "title": "📢 Czas na odrobinę propagandy!",
                "description": f"### *{quote}*",
                "color": 3447003,  # Soft Blue
                "footer": {
                    "text": f"Historical Archive Bot • Quotes remaining today: {remaining_today}"
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
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
    print(f"Quiet hours: {QUIET_HOURS_START}:00 - {QUIET_HOURS_END}:00")

    last_reset_date = None
    schedule = []

    try:
        while True:
            try:
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

            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] UNEXPECTED ERROR in main loop: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)
                continue

            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Bot shutting down gracefully... Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
