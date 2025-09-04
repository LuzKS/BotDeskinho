import os
import discord
from discord.ext import commands
from discord import app_commands
import discord.ui as ui
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# ⚠️ Coloque aqui o ID do seu servidor
GUILD_ID = 1395761264814325850  # substitua pelo ID do seu servidor

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ------------------------------
# MODAL DE FORMULÁRIO
# ------------------------------
class FormularioModal(ui.Modal):
    def __init__(self, tipo: str, campos: list):
        super().__init__(title=f"{tipo}")
        self.tipo = tipo
        self.inputs = []

        for campo in campos:
            entrada = ui.TextInput(
                label=campo,
                style=discord.TextStyle.paragraph if "Descrição" in campo or "Explicação" in campo else discord.TextStyle.short
            )
            self.add_item(entrada)
            self.inputs.append(entrada)

    async def on_submit(self, interaction: discord.Interaction):
        dados = {inp.label: inp.value for inp in self.inputs}

        try:
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "tipo": self.tipo,
                    "username": interaction.user.name,
                    "user_id": str(interaction.user.id),
                    "dados": dados
                }
            )
            response.raise_for_status()
            await interaction.response.send_message("✅ Solicitação enviada com sucesso!", ephemeral=True)
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"❌ Erro ao enviar: {e}", ephemeral=True)


# ------------------------------
# DROPDOWN DE TIPOS
# ------------------------------
class TipoSolicitacaoSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Solicitações", description="Abrir solicitação genérica"),
            discord.SelectOption(label="Configurar VPN", description="Abrir ticket de VPN"),
            discord.SelectOption(label="Criar Máquina Virtual", description="Solicitar VM"),
            discord.SelectOption(label="Criar Pipeline", description="Solicitar pipeline"),
        ]
        super().__init__(placeholder="Selecione o tipo de solicitação...", options=options, min_values=1, max_values=1)

        self.campos_map = {
            "Solicitações": ["E-mail de contato", "Assunto da solicitação", "Descrição da solicitação"],
            "Configurar VPN": ["E-mail de contato", "Resumo de solicitação", "Nome completo", "Nome de Usuário do Discord", "Sistema Operacional"],
            "Criar Máquina Virtual": ["E-mail de contato", "Resumo de solicitação", "Nome de Usuário do Discord", "Tipo de IP: Externo ou interno", "Explicação das configurações necessárias", "Link do repositório"],
            "Criar Pipeline": ["E-mail de contato", "Resumo de solicitação", "Link do repositório", "Variáveis de ambiente"],
        }

    async def callback(self, interaction: discord.Interaction):
        tipo = self.values[0]
        campos = self.campos_map[tipo]
        await interaction.response.send_modal(FormularioModal(tipo, campos))


class TipoSolicitacaoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TipoSolicitacaoSelect())


# ------------------------------
# SLASH COMMAND
# ------------------------------
@bot.tree.command(
    name="solicitar",
    description="Abrir uma solicitação",
    guild=discord.Object(id=GUILD_ID)  # ⚡ Comando instantâneo no servidor
)
async def solicitar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📋 Selecione o tipo de solicitação:",
        view=TipoSolicitacaoView(),
        ephemeral=True
    )


# ------------------------------
# SYNC AUTOMÁTICO
# ------------------------------
@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        guild = discord.Object(id=GUILD_ID)
        synced_guild = await bot.tree.sync(guild=guild)
        print(f"🏠 Guild {GUILD_ID}: {len(synced_guild)} comandos")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

    print(f"Bot logado como {bot.user}")


bot.run(DISCORD_TOKEN)
