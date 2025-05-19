import os
import discord
import aiohttp
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "fishbot:latest")

OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Save short history of messages per channel or DM
message_histories = defaultdict(lambda: deque(maxlen=6))  # 3 user+bot pairs = 6 messages

async def query_ollama(history):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": history,
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_API_URL, json=payload) as resp:
            logging.info(f"Ollama API status: {resp.status}")
            try:
                data = await resp.json()
                logging.info(f"Ollama API response data: {data}")
                return data.get("message", {}).get("content", "No response")
            except Exception as e:
                logging.error(f"Failed to decode Ollama response: {e}")
                text = await resp.text()
                logging.error(f"Response text: {text}")
                return None

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logging.info('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        logging.info(f"Received message: {message.content}")

        history_key = str(message.channel.id)
        history = message_histories[history_key]

        # Add user's new message
        history.append({"role": "user", "content": message.content})

        async with message.channel.typing():
            response = await query_ollama(list(history))

        if response:
            # Add bot's response to history
            history.append({"role": "assistant", "content": response})
            logging.info(f"Ollama response: {response}")
            await message.channel.send(response)
        else:
            await message.channel.send("Sorry, I got no response from Ollama.")

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
