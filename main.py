import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

# Inicializa o bot com as permissões (intents) necessárias
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
client = discord.Client(intents=intents)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# O evento que dispara quando o bot está online
@client.event
async def on_ready():
    print(f'Bot logado como {client.user}')

# O evento que dispara quando uma nova mensagem é enviada
@client.event
async def on_message(message):
    print(message.author)
    # Ignora mensagens do próprio bot para evitar um loop infinito
    if message.author == client.user:
        return

    # Condição para disparar o webhook.
    if message.content.lower():
        try:
            # Envia uma requisição POST para o webhook do n8n
            response = requests.post(
                WEBHOOK_URL,
                json={"user": message.author.display_name,
                        "user_id": str(message.author.id),
                        "message": message.content,
                        "message_id": str(message.id),
                        "channel_id": str(message.channel.id),
                        "server_id": str(message.guild.id) if message.guild else None
                      }
            )
            response.raise_for_status() # Lança um erro se a requisição falhar
            await message.channel.send("Ticket acionado!")
        except requests.exceptions.RequestException as e:
            await message.channel.send(f"❌ Erro ao acionar o webhook: {e}")

client.run(DISCORD_TOKEN)