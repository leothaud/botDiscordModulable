import sys, sqlite3




def init():
    txt = """token = 
id gestionnaire =
caractère commande =
nom base de données =
"""
    with open('config', 'w') as doc:
        doc.write(txt)

def loadConfig():
    lines = []
    with open('config', 'r') as doc:
        for line in doc:
            lines.append(line[:-1])
    for k in range(len(lines)):
        i = 2
        while (i < len(lines[k]) and lines[k][i-2] != '='):
            i += 1
        if i == len(lines[k]):
            sys.stderr.write("Mauvais fichier de configuration.")
            sys.exit(2)
        lines[k] = lines[k][i:]
    token = lines[0]
    idGestionnaire = int(lines[1])
    startChar = lines[2]
    dbName = lines[3]
    return token, idGestionnaire, startChar, dbName

def createDb(dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("""CREATE TABLE "functions" (
	"id"	INTEGER UNIQUE,
	"nom"	TEXT,
	"args"	TEXT,
	"command"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);""")
    c.execute("""CREATE TABLE "messages" (
	"id"	INTEGER UNIQUE,
	"idMembre"	INTEGER UNIQUE,
	"nombreMessage"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);""")
    c.execute("""CREATE TABLE "reactionMessage" (
        "id"    INTEGER UNIQUE,
        "content"   TEXT,
        "command"   TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
);""")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()
    dbName = input("Entrez le nom de la base de données.\n")
    createDb(dbName)
