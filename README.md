# 📢 Discord Propaganda Bot

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/)

A minimalist Discord bot that automatically sends random quotes (propaganda, historical, or motivational) to your channel using Webhooks. Perfect for bringing some history or humor to your server.

## ✨ Features
- 🚀 **Automatic Scheduling:** The bot randomly picks dispatch times every day.
- 🤫 **Quiet Hours:** Won't disturb you at night (configurable quiet hours).
- 📝 **Simple Quote Base:** Easy content management via a plain text file.
- 🐳 **Docker Ready:** Quick deployment with Docker Compose.
- 🎨 **Rich Embeds:** Aesthetic message layout on Discord.

## 🚀 Quick Start

### 1. Prepare Webhook
- Go to your Discord channel settings -> **Integrations** -> **Webhooks**.
- Create a new Webhook and copy its URL.

### 2. Configuration (.env)
Create a `.env` file in the root directory:
```env
DISCORD_WEBHOOK_URL=your_webhook_url
DAILY_DISPATCH_COUNT=3
QUIET_HOURS_START=23
QUIET_HOURS_END=8
```

### 3. Run (Docker - Recommended)
```bash
docker-compose up -d
```

### 4. Run (Python)
```bash
pip install -r requirements.txt
python propaganda-bot.py
```

## ⚙️ Configuration

| Variable | Description | Default |
|---------|------|-----------|
| `DISCORD_WEBHOOK_URL` | Your Discord Webhook URL (Required) | - |
| `DAILY_DISPATCH_COUNT`| Number of quotes to send per day | `3` |
| `QUIET_HOURS_START`   | Quiet hours start time (0-23) | `23` |
| `QUIET_HOURS_END`     | Quiet hours end time (0-23) | `8` |

## 📂 Quotes File
Add your quotes to the `quotes.txt` file. Each quote should be on a new line.

## 🛠️ Manual Trigger
If you want to send a quote immediately without waiting for the schedule:
```bash
python propaganda_bot.py --now
```

## 🧪 Testing
To run the automated tests:
```bash
pip install pytest
pytest test_bot.py
```
*These tests verify the quiet hour logic and scheduling system.*

---
*Created with ❤️ for Discord communities.*
