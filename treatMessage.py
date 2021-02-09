import discord, asyncio, ast, datetime, sqlite3
import messageCount
from botAPI import *


currentMessage = None
startTime = datetime.datetime.now()

def deGestionnaire(msg, idGestion):
    for role in msg.author.roles:
        if role.id == idGestion:
            return True
    return False




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


async def reactionMessage(msg, dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("SELECT * FROM reactionMessage")
    res = c.fetchall()
    conn.close()
    for react in res:
        if react[1] in msg.content:
            await async_exec(react[2])
    

async def bind(msg, dbName):
    txt = msg.content[1:]
    i = 0
    while i < len(txt) and txt[i] != " ":
        i += 1
    if i != len(txt):
        i += 1
        if txt[i] != "\"":
            await msg.channel.send("ERREUR")
        else:
            n1 = i
            i += 1
            while i < len(txt) and txt[i] != "\"":
                i += 1
            if i != len(txt):
                content = txt[n1+1:i]
                code = txt[i+5:-3]
                conn = sqlite3.connect(dbName)
                c = conn.cursor()
                c.execute("INSERT INTO reactionMessage (content, command) VALUES ('"+content+"','"+code+"');")
                conn.commit()
                conn.close()
                await msg.channel.send("Binding réussis.")
            else:
                await msg.channel.send("ERREUR2")
    else:
        await msg.channel.send("ERREUR3")


async def bindReaction(msg, dbName):
    txt = msg.content[1:]
    i = 0
    while i < len(txt) and txt[i] != " ":
        i += 1
    if i != len(txt):
        i += 1
        n1 = i
        if txt[n1] != "<":
            n2 = n1+1
        else:
            while i < len(txt) and txt[i] != ">":
                i += 1
            if i != len(txt):
                n2 = i+1
            else:
                msg.channel.send("erreur binding")
                return None
        emoji = txt[n1:n2]
        code = txt[n2+4:-3]
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        c.execute("INSERT INTO reactionReaction (content, command) VALUES ('"+emoji+"','"+code+"');")
        conn.commit()
        conn.close()
        await msg.channel.send("Binding réussis.")
    else:
        await msg.channel.send("Erreur binding")

async def treat(msg, dbName, idGestion):
    """
        traite le message reçu
    """
    global startTime
    if msg.content[1:] == "quit":
        await client.change_presence(status=discord.Status.offline)
        await asyncio.sleep(1)
        await client.close()
    elif msg.content[1:] == "uptime":
        await msg.channel.send(str(datetime.datetime.now() - startTime))
    elif msg.content[1:] == "count":
        nbr = messageCount.howMuch(msg.author.id)
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
        elif commandName == "delCommand":
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
                c.execute("DELETE FROM functions WHERE nom='"+functionName+"';")
                conn.commit()
                conn.close()
            else:
                await send("Récupération informations impossibles")
        elif commandName == "addCommand":
            if deGestionnaire(msg, idGestion):
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
        elif commandName == "bind":
            if deGestionnaire(msg, idGestion):
                await bind(msg, dbName)
            else:
                msg.channel.send("Tu n'as pas le droit.")
        elif commandName == "bindReac":
            if deGestionnaire(msg, idGestion):
                await bindReaction(msg, dbName)
            else:
                msg.channel.send("Tu n'as pas le droit.")
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
    

async def reactionReaction(reaction, dbName):
    print(reaction)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("SELECT * FROM reactionReaction")
    res = c.fetchall()
    conn.close()
    for react in res:
        if react[1] == str(reaction):
            await async_exec(react[2])
    
