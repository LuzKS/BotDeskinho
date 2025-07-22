from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
from discord import TextStyle

load_dotenv()  # Carrega variáveis do .env

discord_token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class TicketModal(Modal):
    def __init__(self):
        super().__init__(title="Abrir Ticket")
    
    titulo = TextInput(label="titulo")
    descricao = TextInput(label="descrição", style=TextStyle.long)

    async def on_submit(self, interact:discord.Interaction):
        categoria_ticket = discord.utils.get(interact.guild.categories, id=1397253002607202334)
        ticket_canal = await interact.guild.create_text_channel(F'TICKET-{interact.user.name}', category=categoria_ticket)
        await ticket_canal.set_permissions(interact.user, view_channel=True)
        await ticket_canal.send(f'Ticket criado por {interact.user.mention}\n## Resumo: ## {self.titulo}\nDescrição:\n{self.descricao}')
        await interact.response.send_message(f'Ticket criado em {ticket_canal.mention}', ephemeral=True)



@bot.event
async def on_ready():
    sincs = await bot.tree.sync()
    print(f'{len(sincs)} comandos(s) sincronizado(s)')

@bot.tree.command()
async def abrir_ticket(interaction:discord.Interaction):
    await interaction.response.send_modal(TicketModal())

bot.run(discord_token)