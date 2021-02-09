import discord, asyncio, sqlite3, ast, datetime
import config, messageCount, treatMessage, botAPI


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

test = None

@client.event
async def on_message(msg):
    if msg.author != client.user:
        treatMessage.currentMessage = msg
        messageCount.countMessage(msg, dbName)
        await treatMessage.reactionMessage(msg, dbName)
        if len(msg.content)>0 and msg.content[0] == startChar:
            await treatMessage.treat(msg, dbName, idGestion)
            await msg.add_reaction("\N{lollipop}")

@client.event
async def on_member_join(member):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("INSERT INTO messages (idMembre, nombreMessage) VALUES ("+str(member.id)+",0);")
    conn.commit()
    conn.close()

@client.event
async def on_reaction_add(reaction, user):
    global test
    test = reaction
    if user != client.user:
        await treatMessage.reactionReaction(reaction, dbName)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM messages")
    membersInRows = [elt[1] for elt in rows]
    for mem in client.users:
        if not (mem.id in membersInRows):
            c.execute("INSERT INTO messages (idMembre, nombreMessage) VALUES ("+str(mem.id)+",0);")
    conn.commit()
    conn.close()
    print('-------------------')

@client.event
async def on_error(event, *args, **kwargs):
    await treatMessage.currentMessage.channel.send("Erreur inconnue")

if __name__ == "__main__":
    token, idGestion, startChar, dbName = config.loadConfig()
    client.run(token)
