import discord
import asyncio
import sqlite3

token = None
startChar = '\\'
dbName = "example.db"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)



def nameCommand(msg):
    """
        récupère le nom de la commande
    """
    i = 0
    while ( i < len(msg) and msg[i]!= " "):
        i += 1
    return msg[1:i]

def argsCommand(msg):
    """
        récupère les arguments d'une commande classique.
    """
    i = 0
    while ( i < len(msg) and msg[i]!= " "):
        i += 1
    args = []
    i += 1
    k = i
    while i < len(msg):
        while (i < len(msg) and msg[i] != " "):
            i += 1
        args.append(msg[k:i])
        i += 1
        k = i
    return args

def nameArgs(argsString):
    names = []
    argsString = argsString[1:-1]
    i = 0
    k = 0
    if argsString == "":
        return []
    while i < len(argsString):
        while (i < len(argsString) and argsString[i] != ","):
            i += 1
        names.append(argsString[k:i])
        i += 1
        k = i
    return names
        
    

async def treat(msg):
    """
        traite le message reçu
    """
    if msg.content[1:] == "quit":
        await client.change_presence(status=discord.Status.offline)
        await asyncio.sleep(1)
        await client.close()
    elif msg.content[1:] == "count":
        nbr = howMuch(msg.author.id)
        await msg.channel.send("Tu as envoyé "+str(nbr[0])+" messages.")
    else:
        commandName = nameCommand(msg.content)
        if commandName == "addCommand":
            pass
        else:
            args = argsCommand(msg.content)
            conn = sqlite3.connect(dbName)
            c = conn.cursor()
            c.execute("SELECT nom,args,command FROM functions")
            commands = c.fetchall()
            command = None
            for row in commands:
                if commandName == row[0]:
                    command = row
            if command:
                argsName = nameArgs(command[1])
                if len(argsName) != len(args):
                    await msg.channel.send("Cette commande prend exactement " + str(len(argsName)) + " argument" + ("" if len(argsName)<2 else "s") + ".")
                else:
                    Parameter = {}
                    for i in range(len(argsName)):
                        Parameter[argsName[i]] = eval(args[i])
                    exec(command[2],Parameter)
            else:
                await msg.channel.send("Commande inconnue.")
            conn.close()
    


def countMessage(msg):
    """
        compte les messages des membres
    """
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE messages SET nombreMessage = nombreMessage + 1 WHERE idMembre="+str(msg.author.id)+";")
    conn.commit()
    conn.close()

def howMuch(id):
    """
        envoie un message avec le nombre de messages du membre d'id id
    """
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("SELECT nombreMessage FROM messages WHERE idMembre="+str(id)+";")
    res = c.fetchone()
    conn.close()
    return res
    

def isFromAdmin(msg):
    """
        renvoie vrai ssi le message provient d'un admin sur le serveur.
    """
    return msg.author.guild_permissions.administrator

def tokChan():
    """
        Cette fonction récupère le token du bot et l'id du channel dans un fichier séparé.
    """
    global token
    doc = open('token', 'r')
    lines = []
    for line in doc:
        lines.append(line)
    token = lines[0]

async def main():
    """
        fonction principale du bot.
        écrire ici le code qui s'éxecutera
        à chaque fois.
    """

@client.event
async def on_message(msg):
    """
        Le code ici s'exécute quand le bot voit un nouveau message.
    """
    countMessage(msg)
    if msg.content[0] == startChar:
        await treat(msg)
        await msg.add_reaction("\N{lollipop}")
        
@client.event
async def on_member_join(member):
    """
        Fonction quand un nouveau membre arrive sur le serveur.
    """
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("INSERT INTO messages (idMembre, nombreMessage) VALUES ("+str(member.id)+",0);")
    conn.commit()
    conn.close()

@client.event
async def on_ready():
    """
        Le code ici s'execute quand le bot est pret.
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    conn = sqlite3.connect("example.db")
    c = conn.cursor()
    print('------')
    rows = c.execute('SELECT * FROM messages')
    membersInRows = [elt[1] for elt in rows]
    for mem in client.users:
        if not (mem.id in membersInRows):
            c.execute("INSERT INTO messages (idMembre, nombreMessage) VALUES ("+str(mem.id)+",0);")
    conn.commit()
    conn.close()
        
    

if __name__=="__main__":
    tokChan()
    #client.loop.create_task(main())
    client.run(token)
