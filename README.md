# Discord Chatbot with Ollama Integration

This is a lightweight Discord chatbot powered by [Ollama](https://ollama.com), designed to run locally using your own language models. It listens for mentions or direct messages, maintains short-term context, and streams intelligent responses back to users.

## Features

* 💬 Responds to @mentions and direct messages
* 🧠 Maintains context of the last 3 user messages per conversation
* ⌛ Displays typing indicator while generating replies
* 📚 Uses any model available in your local Ollama instance
* 🛠️ Simple to configure and deploy with Docker

## Requirements

* Python 3.10+
* Docker (for deployment)
* A running Ollama server with a compatible model loaded (e.g. `llama3`, `mistral`, etc.)
* A Discord bot token

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/discord-ollama-bot.git
cd discord-ollama-bot
```

### 2. Set environment variables

When deploying with Docker or Portainer, set the following environment variables:

| Variable        | Description                                                   |
| --------------- | ------------------------------------------------------------- |
| `DISCORD_TOKEN` | Your Discord bot token                                        |
| `OLLAMA_HOST`   | Host where Ollama is running (default: `localhost`)           |
| `OLLAMA_PORT`   | Ollama server port (default: `11434`)                         |
| `OLLAMA_MODEL`  | The model name (e.g. `llama3`, `mistral`, `yourmodel:latest`) |

### 3. Build and run with Docker

You can use the following `docker-compose.yml`:

```yaml
version: '3.8'

services:
  discord-bot:
    build: .
    environment:
      - DISCORD_TOKEN
      - OLLAMA_HOST
      - OLLAMA_PORT
      - OLLAMA_MODEL
    restart: unless-stopped
```

If using Portainer, upload your environment variables manually or via a `.env`/`stack.env` file.

### 4. Configure Discord Bot

* Enable the **Message Content Intent** under the bot settings on the [Discord Developer Portal](https://discord.com/developers/applications)
* Invite the bot with at least the following permission scopes:

  * `bot`
  * `messages.read`
  * `messages.send`
  * `message_content`

Minimum bot permission integer: `3072` (Send Messages + Read Message History)

## Example

Mention the bot in any channel or send it a DM:

```
@YourBot What's the weather like on Mars?
```

It will use the last 3 messages as context to improve reply relevance.

## License

MIT License. Feel free to use, modify, and share.
