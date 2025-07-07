
import sqlite3
from flask import Flask, render_template, request, session, redirect, flash, jsonify, url_for
import db
from werkzeug.exceptions import abort
from flask_compress import Compress
from db import getAllFlavours, addDrink, getLoggedFlavours

app = Flask(__name__)
Compress(app)
app.secret_key = "munt"

@app.route("/")
def Home():
    conn = sqlite3.connect('.database/flavors.db')  # Make sure this path is correct
    conn.row_factory = sqlite3.Row  # To access rows like dicts
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours
        WHERE totalDrinks > 0;
    """)
    flavours = cursor.fetchall()
    conn.close()
    return render_template("index.html", flavours=flavours)



@app.route('/add', methods=['GET', 'POST'])
def add():
    flavour = request.form.get('flavour')

    if request.method == 'POST':
        flavour = request.form['flavour']
        conn = sqlite3.connect('.database/flavors.db')
        cursor = conn.cursor()
        # Increment totalDrinks and update totalCaffeine
        cursor.execute("""
            UPDATE flavours
            SET totalDrinks = totalDrinks + 1,
                totalCaffeine = caffeine * (totalDrinks + 1)
            WHERE flavour = ?;
        """, (flavour,))
        conn.commit()
        conn.close()
        return redirect('/')  # redirect to drinks list

    return render_template('add.html') 

@app.route("/stats")
def stats():
    conn = sqlite3.connect('.database/flavors.db')
    cursor = conn.cursor()
    flavours = getLoggedFlavours()  # Only those with totalDrinks > 0

    
    

    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours
        ORDER BY totalDrinks DESC;
    """)
    stats_data = cursor.fetchall()
    conn.close()
    
    return render_template("stats.html", flavours=flavours)

    return render_template("stats.html", flavours=stats_data)

@app.route('/ranks')
def ranks():
    conn = sqlite3.connect('.database/flavors.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flavour, COUNT(*) as total
        FROM flavours
        WHERE totalDrinks > 0
        GROUP BY flavour
        ORDER BY totalDrinks DESC
    """)
    ranks = cursor.fetchall()  # List of (flavour, total)

    conn.close()
    return render_template('ranks.html', ranks=ranks)

app.run(debug=True, port=5000)