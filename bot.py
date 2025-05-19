import os
import discord
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "fishbot:latest")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def query_ollama(message_content):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": message_content}],
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_API_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("message", {}).get("content", "No response")
            else:
                return f"Error from Ollama API: {resp.status}"

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
        response = await query_ollama(message.content)
        logging.info(f"Ollama response: {response}")
        await message.channel.send(response)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
