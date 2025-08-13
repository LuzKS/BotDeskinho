import os
import base64
import requests
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Select, View
from discord import TextStyle
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
USER_EMAIL = os.getenv("USER_EMAIL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIRA_REQUEST_TYPES = os.getenv("JIRA_REQUEST_TYPES")
JIRA_API_REQUEST = os.getenv("JIRA_API_REQUEST")

# Função para autenticação Jira
def get_jira_auth_header():
    auth_str = f"{USER_EMAIL}:{JIRA_TOKEN}"
    base64_string = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {base64_string}"
    }

# Função para buscar requestTypes do Jira
def get_request_types():
    url = JIRA_REQUEST_TYPES
    headers = get_jira_auth_header()
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "helpText": item["helpText"]
            }
            for item in data.get("values", [])
        ]
    else:
        print("Erro ao buscar request types:", response.status_code)
        return []

# Função para criar um ticket no Jira
def criar_ticket_jira(request_type_id, summary, description):
    url = JIRA_API_REQUEST
    headers = get_jira_auth_header()
    payload = {
        "serviceDeskId": "1",
        "requestTypeId": request_type_id,
        "requestFieldValues": {
            "summary": summary,
            "description": description
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in (200, 201):
        return response.json()
    else:
        print("Erro ao criar ticket no Jira:", response.status_code, response.text)
        return None

# Modal customizado baseado no tipo de request
class TicketModalComTipo(Modal):
    def __init__(self, request_type):
        super().__init__(title=request_type['name'])
        self.request_type = request_type

        self.titulo = TextInput(label="Título do ticket")
        self.descricao = TextInput(label=request_type.get('helpText') or "Descrição", style=TextStyle.long)
        self.add_item(self.titulo)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        categoria_ticket = discord.utils.get(interaction.guild.categories, id=834513064451506186) 
        canal = await interaction.guild.create_text_channel(f'TICKET-{interaction.user.name}', category=categoria_ticket)
        await canal.set_permissions(interaction.user, view_channel=True)

        await canal.send(f"Ticket criado por {interaction.user.mention}\n### Tipo: {self.request_type['name']}\nResumo: {self.titulo}\nDescrição:\n{self.descricao}")

        # Criar ticket no Jira
        jira_response = criar_ticket_jira(
            request_type_id=self.request_type["id"],
            summary=str(self.titulo),
            description=str(self.descricao)
        )

        if jira_response:
            issue_key = jira_response.get("issueKey", "desconhecido")
            await canal.send(f"🎫 Ticket Jira criado com sucesso: **{issue_key}**")
        else:
            await canal.send("❌ Falha ao criar ticket no Jira.")

        await interaction.response.send_message(f'Ticket criado: {canal.mention}', ephemeral=True)

# Select dinâmico baseado nos requestTypes
class RequestTypeSelect(Select):
    def __init__(self, options, request_types):
        super().__init__(placeholder="Escolha um tipo de request", min_values=1, max_values=1, options=options)
        self.request_types = request_types

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        selected_request = next(rt for rt in self.request_types if rt["id"] == selected_id)
        await interaction.response.send_modal(TicketModalComTipo(selected_request))

class RequestTypeView(View):
    def __init__(self, request_types):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(label=rt["name"], value=rt["id"], description=rt["description"][:100])
            for rt in request_types
        ]
        self.add_item(RequestTypeSelect(options, request_types))

# Bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    sincs = await bot.tree.sync()
    print(f'{len(sincs)} comando(s) sincronizado(s)')

@bot.tree.command(name="abrir_ticket")
async def abrir_ticket(interaction: discord.Interaction):
    request_types = get_request_types()
    if not request_types:
        await interaction.response.send_message("Erro ao buscar tipos de request do Jira.", ephemeral=True)
        return
    view = RequestTypeView(request_types)
    await interaction.response.send_message("Escolha o tipo de ticket que deseja abrir:", view=view, ephemeral=True)

bot.run(DISCORD_TOKEN)
