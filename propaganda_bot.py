import argparse
import logging
import os
import random
import sys
import time
from datetime import UTC, datetime, timedelta
from typing import List

import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Configuration
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
QUOTES_FILE = "quotes.txt"
# Load daily dispatch count from environment variable, default to 3
try:
    DAILY_DISPATCH_COUNT = int(os.getenv("DAILY_DISPATCH_COUNT", "3"))
except ValueError:
    logger.warning("Invalid DAILY_DISPATCH_COUNT in .env. Defaulting to 3.")
    DAILY_DISPATCH_COUNT = 3

# Quiet Hours configuration
try:
    QUIET_HOURS_START = int(os.getenv("QUIET_HOURS_START", "23"))
    QUIET_HOURS_END = int(os.getenv("QUIET_HOURS_END", "8"))
except ValueError:
    logger.warning("Invalid QUIET_HOURS configuration in .env. Defaulting to 23-8.")
    QUIET_HOURS_START = 23
    QUIET_HOURS_END = 8


def is_quiet_hour(hour: int, start: int, end: int) -> bool:
    """Checks if the given hour falls within the quiet hours range."""
    if start < end:
        return start <= hour < end
    else:  # Range crosses midnight (e.g., 23 to 8)
        return hour >= start or hour < end


def load_quotes() -> List[str]:
    """Loads quotes from the external text file."""
    if not os.path.exists(QUOTES_FILE):
        logger.error(f"File {QUOTES_FILE} does not exist.")
        return []

    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes


def generate_schedule(count: int = 3) -> List[datetime]:
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


def send_to_discord(quote: str, remaining_today: int | str = 0) -> None:
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
            logger.info("Message sent successfully.")
        else:
            logger.error(f"Webhook Error: status {response.status_code}")
            logger.error(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"Connection problem: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Discord Propaganda Bot")
    parser.add_argument(
        "--now", action="store_true", help="Send a quote immediately and exit"
    )
    args = parser.parse_args()

    # Strict check for the Webhook URL
    if not WEBHOOK_URL:
        logger.critical("DISCORD_WEBHOOK_URL environment variable not found!")
        logger.info("Ensure you have a .env file with: DISCORD_WEBHOOK_URL=your_url")
        sys.exit(1)

    quotes = load_quotes()
    if not quotes:
        logger.critical("No quotes to send. Shutting down.")
        sys.exit(1)

    if args.now:
        selected_quote = random.choice(quotes)
        logger.info("Manual trigger: sending quote now...")
        send_to_discord(selected_quote, remaining_today="N/A (Manual Trigger)")
        sys.exit(0)

    logger.info("Initializing bot...")
    logger.info(f"Configured daily dispatch count: {DAILY_DISPATCH_COUNT}")
    logger.info(f"Quiet hours: {QUIET_HOURS_START}:00 - {QUIET_HOURS_END}:00")

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
                    logger.info(f"--- New Day: {current_date} ---")
                    logger.info(f"Schedule: {[t.strftime('%H:%M:%S') for t in schedule]}")

                for scheduled_time in schedule[:]:
                    if now >= scheduled_time:
                        selected_quote = random.choice(quotes)
                        schedule.remove(scheduled_time)
                        logger.info(f"Sending for scheduled time {scheduled_time.strftime('%H:%M:%S')}")
                        send_to_discord(selected_quote, remaining_today=len(schedule))

            except Exception as e:
                logger.error(f"UNEXPECTED ERROR in main loop: {e}")
                logger.info("Retrying in 60 seconds...")
                time.sleep(60)
                continue

            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully... Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
