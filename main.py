import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # deixa o bot ler o conteúdo das mensagens
client = discord.Client(intents=intents)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


@client.event
async def on_ready():
    print(f'Bot logado como {client.user}')



@client.event
async def on_message(message):
    print(message.author)
    print(message.channel)
    # ignora mensagens do próprio bot para evitar um loop infinito
    if message.author == client.user:
        return

    if message.content.lower():
        if str(message.channel) == "comandos":
            try:
                # envia uma requisição POST para o webhook do n8n
                response = requests.post(
                    WEBHOOK_URL,
                    json={  "username": message.author.name,
                            "user": message.author.display_name,
                            "user_id": str(message.author.id),
                            "message": message.content,
                            "message_id": str(message.id),
                            "channel_id": str(message.channel.id),
                            "server_id": str(message.guild.id) if message.guild else None
                        }
                )
                response.raise_for_status() 
                await message.channel.send("Ticket acionado!")
            except requests.exceptions.RequestException as e:
                await message.channel.send(f"❌ Erro ao acionar o webhook: {e}")

client.run(DISCORD_TOKEN)