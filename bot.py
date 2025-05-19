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

# Store recent message history for context
message_history = []

async def query_ollama():
    payload = {
        "model": OLLAMA_MODEL,
        "messages": message_history[-3:],  # use last 3 messages
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

        # Add to message history
        message_history.append({"role": "user", "content": message.content})

        async with message.channel.typing():
            response = await query_ollama()
            logging.info(f"Ollama response: {response}")

            # Add assistant response to history
            message_history.append({"role": "assistant", "content": response})

            # Split and send if longer than 2000 characters
            for chunk in [response[i:i+2000] for i in range(0, len(response), 2000)]:
                await message.channel.send(chunk)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
