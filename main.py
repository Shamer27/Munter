import sqlite3
from flask import Flask, render_template, request, session, redirect, flash, jsonify
import db
from werkzeug.exceptions import abort
from flask_compress import Compress

app = Flask(__name__)
Compress(app)
app.secret_key = "munt"

@app.route("/")
def Home():
    conn = sqlite3.connect('flavors.db')  # Make sure this path is correct
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
def add_drink():
    if request.method == 'POST':
        flavour = request.form['flavour']
        conn = sqlite3.connect('flavors.db')
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

@app.route('/stats')
def stats():
    conn = sqlite3.connect('flavors.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours
        ORDER BY totalDrinks DESC;
    """)
    stats_data = cursor.fetchall()
    conn.close()

    return render_template("stats.html", flavours=stats_data)

app.run(debug=True, port=5000)