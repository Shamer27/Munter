import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def GetDB():

    # Connect to the database and return the connection object
    db = sqlite3.connect(".database/flavors.db")
    db.row_factory = sqlite3.Row

    return db

def getAllFlavours():
    db = GetDB()
    flavors = db.execute("SELECT * FROM flavours").fetchall()
    db.close()
    return flavors



def addDrink(flavour):
   
    # Check if any boxes were empty
    if flavour is None:
        return False
   
    # Get the DB and add the guess
    db = GetDB()
    
    db.execute("""UPDATE flavours
                SET 
                    totalDrinks = totalDrinks + 1, totalCaffeine = caffeine * (totalDrinks + 1)
                WHERE 
                    flavour = addedFlavour;""")
    db.commit()
    return True

def getLoggedFlavours():
    db = GetDB()
    logged = db.execute("""
        SELECT flavour, caffeine, size, totalCaffeine, totalDrinks
        FROM flavours
        WHERE totalDrinks > 0
        ORDER BY totalDrinks DESC
    """).fetchall()
    db.close()
    return logged