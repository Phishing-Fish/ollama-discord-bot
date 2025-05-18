FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build tools and dependencies
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libssl-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . .

# Run the bot
CMD ["python", "bot.py"]
