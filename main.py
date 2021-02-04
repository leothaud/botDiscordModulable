import discord
import asyncio

channel = None
token = None
startChar = '\\'

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

def isFromAdmin(message):
    return message.author.guild_permissions.administrator

def tokChan():
    """
        Cette fonction récupère le token du bot et l'id du channel dans un fichier séparé.
    """
    global channel
    global token
    doc = open('token', 'r')
    lines = []
    for line in doc:
        lines.append(line)
    token = lines[0]
    channel = int(lines[1])

async def main():
    """
        fonction principale du bot.
    """
    global channel
    await asyncio.sleep(5)

@client.event
async def on_message(message):
    if message.content[0] == startChar:
        await message.add_reaction("\N{lollipop}")
    
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')



if __name__=="__main__":
    tokChan()
    client.loop.create_task(main())
    client.run(token)
