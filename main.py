import sqlite3
from flask import Flask, render_template, request, session, redirect, flash, jsonify, url_for
import db
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
import io
import base64
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
        WHERE totalDrinks > 0
        ORDER BY totalDrinks DESC;
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

@app.route('/stats')
def stats():
    import matplotlib.pyplot as plt
    import io
    import base64
    import sqlite3
    
    flavour_colors = {
        'Absolutely Zero': '#888888',
        'Assault': '#b71c1c',
        'Aussie Style Lemonade': '#888888',
        'Ballers Blend': '#888888',
        'Black': '#000000',
        'Black Ice': '#888888',
        'Blue': '#2196f3',
        'Cuba-Libre': '#888888',
        'Cuba-Lima': '#888888',
        'DUB Edition': '#888888',
        'Fury': '#888888',
        'Ghost M-100': '#888888',
        'Gold': '#ffd700',
        'Green': '#4caf50',
        'Gronk': '#888888',
        'Heavy Metal': '#888888',
        'Import': '#888888',
        'Java Big Black': '#888888',
        'Java Café Latte': '#888888',
        'Java Café Mocha': '#888888',
        'Java Cold Brew Latte': '#888888',
        'Java Cold Brew Sweet Black': '#888888',
        'Java Farmers Oats': '#888888',
        'Java French Vanilla': '#888888',
        'Java Irish Blend': '#bfa980',
        'Java Kona Blend': '#888888',
        'Java Loca Moca': '#888888',
        'Java Mean Bean': '#cdb79e',
        'Java Oatmilk Latte': '#888888',
        'Java Oatmilk Mocha': '#888888',
        'Java Salted Caramel': '#cfa36c',
        'Java Swiss Chocolate': '#888888',
        'Juiced Aussie Style Lemonade': '#fff176',
        'Juiced Khaotic': '#888888',
        'Juiced Khaotic (Tropical Orange)': '#888888',
        'Juiced Mango Loco': '#ff9f00',
        'Juiced Monarch': '#fbb13c',
        'Juiced Papillon': '#edc0bf',
        'Juiced Rio Punch': '#888888',
        'Khaos': '#888888',
        'Lewis Hamilton 44': '#d4af37',
        'Lewis Hamilton Zero Sugar': '#888888',
        'Lo-Carb': '#0d47a1',
        'M-80': '#888888',
        'MIXXD': '#888888',
        'Mad Dog': '#888888',
        'Mango Loco': '#ff9f00',
        'Nitro Anti-Gravity': '#888888',
        'Nitro Black Ice': '#1e1e1e',
        'Nitro Cosmic Apple': '#888888',
        'Nitro Cosmic Berry': '#888888',
        'Nitro Cosmic Berry Lemonade': '#888888',
        'Nitro Cosmic Birthday Cake': '#888888',
        'Nitro Cosmic Blue Raspberry': '#888888',
        'Nitro Cosmic Bubblegum': '#888888',
        'Nitro Cosmic Candy Corn': '#888888',
        'Nitro Cosmic Cherry': '#888888',
        'Nitro Cosmic Cherry Limeade': '#888888',
        'Nitro Cosmic Citrus': '#888888',
        'Nitro Cosmic Citrus Punch': '#888888',
        'Nitro Cosmic Cotton Candy': '#888888',
        'Nitro Cosmic Dragonfruit': '#888888',
        'Nitro Cosmic Fruit Punch': '#888888',
        'Nitro Cosmic Grape': '#888888',
        'Nitro Cosmic Kiwi': '#888888',
        'Nitro Cosmic Lime': '#888888',
        'Nitro Cosmic Lychee': '#888888',
        'Nitro Cosmic Mango': '#888888',
        'Nitro Cosmic Marshmallow': '#888888',
        'Nitro Cosmic Orange': '#888888',
        'Nitro Cosmic Passionfruit': '#888888',
        'Nitro Cosmic Peach': '#888888',
        'Nitro Cosmic Pineapple': '#888888',
        'Nitro Cosmic Strawberry': '#888888',
        'Nitro Cosmic Tropical Punch': '#888888',
        'Nitro Cosmic Watermelon': '#888888',
        'Nitro Cosmic Yuzu': '#888888',
        'Nitro Killer B': '#888888',
        'Nitro Super Dry': '#c0c0c0',
        'Original': '#2e7d32',
        'Pacific Punch': '#e4572e',
        'Phantom M-100': '#888888',
        'Pink': '#ec407a',
        'Pipeline Punch': '#888888',
        'Red': '#f44336',
        'Rehab Green Tea': '#81c784',
        'Rehab Lemonade': '#f4e04d',
        'Rehab Orangeade': '#888888',
        'Rehab Peach Tea': '#f8b195',
        'Rehab Pink Lemonade': '#888888',
        'Rehab Protean': '#888888',
        'Rehab Rojo Tea': '#888888',
        'Reserve Kiwi Strawberry': '#888888',
        'Reserve Orange Dreamsicle': '#888888',
        'Reserve Peaches N Crème': '#888888',
        'Reserve Watermelon': '#888888',
        'Reserve White Pineapple': '#888888',
        'Ripper': '#888888',
        'The Doctor VR46': '#ffd700',
        'Ultra Arctic': '#888888',
        'Ultra Black': '#888888',
        'Ultra Black Cherry': '#888888',
        'Ultra Blue': '#4a90e2',
        'Ultra Blue Hawaii': '#888888',
        'Ultra Chill': '#888888',
        'Ultra Citron': '#ffeb3b',
        'Ultra Cosmic': '#888888',
        'Ultra Dragonfruit': '#888888',
        'Ultra Eclipse': '#888888',
        'Ultra Fiesta': '#ffa726',
        'Ultra Fiesta Mango': '#888888',
        'Ultra Frost': '#888888',
        'Ultra Galaxy': '#888888',
        'Ultra Grape': '#888888',
        'Ultra Green Apple': '#888888',
        'Ultra Ice': '#888888',
        'Ultra Kiwi Lime': '#888888',
        'Ultra Lemon Ice': '#888888',
        'Ultra Lychee': '#888888',
        'Ultra Moonlight': '#888888',
        'Ultra Nova': '#888888',
        'Ultra Paradise': '#66bb6a',
        'Ultra Peachy Keen': '#ffc0cb',
        'Ultra Red': '#c42126',
        'Ultra Rosa': '#f95a9b',
        'Ultra Sakura': '#888888',
        'Ultra Strawberry Dreams': '#ff99cc',
        'Ultra Sunrise': '#ffa726',
        'Ultra Violet': '#7e57c2',
        'Ultra Violet Storm': '#888888',
        'Ultra Watermelon': '#ff5e78',
        'Ultra White Pineapple': '#888888',
        'Ultra Yuzu': '#888888',
        'Unleaded': '#888888',
        'White': '#ffffff',
        'Zero Ultra (white)': '#ffffff'
    }
    conn = sqlite3.connect('./.database/flavors.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours
        WHERE totalDrinks > 0
        ORDER BY totalDrinks DESC;
    """)
    results = cursor.fetchall()
    conn.close()

    total_value = sum(row['totalCaffeine'] for row in results)
    total_drinks = sum(row['totalDrinks'] for row in results)

    # Group data
    main_flavours = []
    other_drinks = 0

    for row in results:
        if row['totalDrinks'] >= 3:
            main_flavours.append({'flavour': row['flavour'], 'totalDrinks': row['totalDrinks']})
        else:
            other_drinks += row['totalDrinks']

    if other_drinks > 0:
        main_flavours.append({'flavour': 'Other', 'totalDrinks': other_drinks})

    # Prepare pie chart
    labels = [item['flavour'] for item in main_flavours]
    values = [item['totalDrinks'] for item in main_flavours]
    colors = [flavour_colors.get(label, '#888888') for label in labels]

    fig, ax = plt.subplots(figsize=(7, 7))
    
    fig.patch.set_facecolor('#0D1B2A')  # Set background color
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        pctdistance=0,
        startangle=140,
        textprops={"color": "black"}
    )
    ax.axis("equal")

    # Save to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    pie_chart_uri = f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
    buf.close()
    plt.close(fig)

    return render_template("stats.html", 
                           flavours=results,
                           total_value=total_value,
                           total_drinks=total_drinks,
                           pie_chart=pie_chart_uri)
    

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