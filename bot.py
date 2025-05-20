import os
import discord
import aiohttp
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "your-model-name:latest")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Store recent conversation history per user
conversation_history = {}

async def query_ollama(user_id, username, new_message):
    history = conversation_history.get(user_id, deque(maxlen=3))

    # Create chat format for Ollama API
    chat_messages = list(history)
    chat_messages.append({"role": "user", "content": f"{username} says: {new_message}"})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": chat_messages,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_API_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data.get("message", {}).get("content", "No response")

                # Add the user's message and model's reply to history
                history.append({"role": "user", "content": f"{username} says: {new_message}"})
                history.append({"role": "assistant", "content": response})
                conversation_history[user_id] = history

                return response
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

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mention = client.user in message.mentions

    if is_dm or is_mention:
        logging.info(f"Received message: {message.content}")

        # Remove bot mention from the message content
        cleaned_content = message.content.replace(f"<@{client.user.id}>", "").strip()

        async with message.channel.typing():
            response = await query_ollama(
                user_id=message.author.id,
                username=message.author.display_name,
                new_message=cleaned_content
            )

        # Split long messages if needed
        if len(response) <= 2000:
            await message.channel.send(response)
        else:
            for chunk in [response[i:i+2000] for i in range(0, len(response), 2000)]:
                await message.channel.send(chunk)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
