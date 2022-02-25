from database import Champions


db = Champions()

for c in db.load_champs():
    print(c)