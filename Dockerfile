# Use a lightweight base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Prevent Python from buffering logs (visible immediately in docker logs)
ENV PYTHONUNBUFFERED=1

# Copy dependency files and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY propaganda_bot.py .
COPY quotes.txt .

# Run the bot
CMD ["python", "propaganda_bot.py"]
