import discord
import asyncio
import sqlite3
import ast


token = None
idGestion = None
startChar = '\\'
dbName = "example.db"
currentMessage = None

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

def deGestionnaire(msg):
    global idGestion
    roles = msg.author.roles
    res = False
    for role in roles:
        if role.id == idGestion:
            res = True
    return res
    

async def async_exec(stmts, env=None):
    parsed_stmts = ast.parse(stmts)

    fn_name = "_async_exec_f"

    fn = f"async def {fn_name}(): pass"
    parsed_fn = ast.parse(fn)

    for node in parsed_stmts.body:
        ast.increment_lineno(node)

    parsed_fn.body[0].body = parsed_stmts.body
    exec(compile(parsed_fn, filename="<ast>", mode="exec"), env)

    return await eval(f"{fn_name}()", env)

async def send(text):
    global currentMessage
    n = len(text)//2000
    for i in range(n+1):
        tmp = text[2000*i:2000*(i+1)]
        await currentMessage.channel.send(tmp)

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
        

# \command (n0)nom (n1)[fkgfkdpgf](n2)   

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
    elif msg.content[1:] == "listCommand":
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        c.execute("SELECT nom FROM functions;")
        liste = c.fetchall()
        text = ""
        for elt in liste:
            text += elt[0]+"\n"
        await send(text)
        conn.close()
    else:
        commandName = nameCommand(msg.content)
        if commandName == "infoCommand":
            i = 0
            while (i < len(msg.content) and msg.content[i] != " "):
                i += 1
            if i != len(msg.content):
                i += 1
                n0 = i
                while (i < len(msg.content) and msg.content[i] != " "):
                    i += 1
                functionName = msg.content[n0:i]
                conn = sqlite3.connect(dbName)
                c = conn.cursor()
                c.execute("SELECT * FROM functions WHERE nom='"+functionName+"';")
                res = c.fetchone()
                if res == None:
                    await send("Commande "+functionName+" introuvable.")
                else:
                    await send(res[1]+" "+res[2]+" : ```"+res[3]+"```")
            else:
                await send("Récupération informations impossibles")
        elif commandName == "addCommand":
            if deGestionnaire(msg):
                i = 0
                while (i < len(msg.content) and msg.content[i] != " "):
                    i += 1
                if i != len(msg.content):
                    i += 1
                    n0 = i
                    while (i < len(msg.content) and msg.content[i] != " "):
                        i += 1
                    if i != len(msg.content):
                        i += 1
                        n1 = i
                        while (i < len(msg.content) and msg.content[i] != " "):
                            i += 1
                        if i != len(msg.content):
                            i += 1
                            n2 = i
                            functionName = msg.content[n0:n1-1]
                            functionArgs = msg.content[n1:n2-1]
                            function = msg.content[n2+3:-3]
                            conn = sqlite3.connect(dbName)
                            c = conn.cursor()
                            c.execute("SELECT COUNT(*) FROM functions WHERE nom=\'"+functionName+"\';")
                            res = c.fetchone()
                            if res[0] == 0:
                                c.execute("INSERT INTO functions (nom, args, command) VALUES (\'"+functionName+"\',\'"+functionArgs+"\',\'"+function+"\');")
                                conn.commit()
                                await send("Fonction "+functionName+" ajoutée avec succès.")
                            else:
                                await send("Fonction "+functionName+" déjà existante.")
                            conn.close()
                        else:
                            await msg.channel.send("Cette commande prend comme arguments le nom de la fonction, la liste des arguments puis la fonction entre `.")
                    else:
                        await msg.channel.send("Cette commande prend comme arguments le nom de la fonction, la liste des arguments puis la fonction entre `.")
                else:
                    await msg.channel.send("Cette commande prend comme arguments le nom de la fonction, la liste des arguments puis la fonction entre `.")
            else:
                await msg.channel.send("Tu n'as pas le droit.")
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
                    Parameter = dict(globals())
                    for i in range(len(argsName)):
                        Parameter[argsName[i]] = eval(args[i])
                    await async_exec(command[2],Parameter)
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
    global idGestion
    doc = open('token', 'r')
    lines = []
    for line in doc:
        lines.append(line)
    token = lines[0]
    idGestion = int(lines[1])

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
    global currentMessage
    countMessage(msg)
    if len(msg.content)>0 and msg.content[0] == startChar:
        currentMessage = msg
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
