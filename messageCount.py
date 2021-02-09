import sqlite3, discord

def countMessage(msg, dbName):
    """
        compte les messages des membres
    """
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE messages SET nombreMessage = nombreMessage + 1 WHERE idMembre="+str(msg.author.id)+";")
    conn.commit()
    conn.close()

def howMuch(idMembre, dbName):
    """
        envoie un message avec le nombre de messages du membre d'id id
    """
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("SELECT nombreMessage FROM messages WHERE idMembre="+str(idMembre)+";")
    res = c.fetchone()
    conn.close()
    return res
