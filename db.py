import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def GetDB():

    # Connect to the database and return the connection object
    db = sqlite3.connect(".database/flavors.db")
    db.row_factory = sqlite3.Row

    return db

def get():

    # Connect, query all guesses and then return the data
    db = GetDB()
    flavors = db.execute("""SELECT flavours.flavour, flavours.caffeine, flavours.size, flavours.totalCaffeine, flavours.totalDrinks FROM flavours
                         ORDER BY totalDrinks DESC""").fetchall()
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

def getSingleReview(id):

    db = GetDB()
    flavour = db.execute(f"SELECT * FROM flavour WHERE id={id}").fetchone()
    db.close()

    return flavour