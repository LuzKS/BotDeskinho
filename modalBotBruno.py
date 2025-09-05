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


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


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
        GUILD_ID = interaction.guild.id

        try:
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "tipo": self.tipo,
                    "username": interaction.user.name,
                    "user_id": str(interaction.user.id),
                    "channel_id": str(interaction.channel.id),
                    "server_id": str(interaction.guild.id) if interaction.guild else None,
                    "dados": dados
                }
            )

            response.raise_for_status()
            await interaction.response.send_message("✅ Solicitação enviada com sucesso!", ephemeral=True)
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"❌ Erro ao enviar: {e}", ephemeral=True)


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
            "Solicitações": [ "Resumo de solicitação", "Descrição da solicitação"],
            "Configurar VPN": [ "Resumo de solicitação", "Nome completo", "Sistema Operacional"],
            "Criar Máquina Virtual": ["Resumo de solicitação", "Tipo de IP: Externo ou interno", "Explicação das configurações necessárias", "Link do repositório"],
            "Criar Pipeline": ["Resumo de solicitação", "Link do repositório", "Variáveis de ambiente"],
        }

    async def callback(self, interaction: discord.Interaction):
        tipo = self.values[0]
        campos = self.campos_map[tipo]
        await interaction.response.send_modal(FormularioModal(tipo, campos))


class TipoSolicitacaoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TipoSolicitacaoSelect())



@bot.tree.command(
    name="solicitar",
    description="Abrir uma solicitação",
)

async def solicitar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📋 Selecione o tipo de solicitação:",
        view=TipoSolicitacaoView(),
        ephemeral=True
    )



@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        sincs = await bot.tree.sync()
        print(f"{len(sincs)} comando(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

    print(f"Bot logado como {bot.user}")


bot.run(DISCORD_TOKEN)