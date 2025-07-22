import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env

discord_token = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.all() #permissoes do discord
bot = commands.Bot("/", intents=intents) #contem todas as informações do bot


@bot.event
async def on_ready():
    sincs = await bot.tree.sync()
    print(f'{len(sincs)} comandos(s) sincronizado(s)')


@bot.command()
async def teste(ctx:commands.Context, *,argumento): # o * faz pegar toda a informacao
    nome = ctx.author.name
    argumento = argumento
    await ctx.reply(f"Olá, {nome}. Em que posso ajudar? '{argumento}' não é um pedido válido") #o .reply responde diretamente ao comando
    await ctx.send(f"Olá, {nome}. Em que posso ajudar?") #responde direto no chat, sem marcar a msg

@bot.command()
async def soma(ctx:commands.Context, num1:int, num2:int):
    num1= num1
    num2= num2
    soma = num1 + num2
    await ctx.send(f'o resultado da soma é: {soma}')

@bot.command()
async def bom_dia(ctx:commands.Context):
    nome = ctx.author.name
    mEmbed = discord.Embed()
    mEmbed.title= f"Bom dia, {nome}!"
    mEmbed.description = "Lembra de tomar seu café."

    imagem = discord.File("imagem.jpg", "imagem.jpg")
    mEmbed.set_image(url="attachment://imagem.jpg")

    await ctx.send(embed=mEmbed, file=imagem)


@bot.event
async def on_member_join(membro:discord.Member):
    canal = bot.get_channel(1397007052097978369)
    await canal.send(f'{membro.mention} bem vindo ao teste testeiro!')

@bot.tree.command()
async def vish(interact:discord.Interaction, texto:str):
    await interact.response.send_message(f"kk, {texto}")




bot.run(discord_token)
