import sqlite3
import uuid
import os
from flask import Flask, render_template, make_response, request, redirect, url_for
from flask_compress import Compress
import matplotlib
matplotlib.use('Agg')  # safe on servers without display

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = globals().get("DB_PATH") or os.path.join(BASE_DIR, ".database", "flavors.db")  # <-- adjust if your DB is elsewhere

app = Flask(__name__)
Compress(app)
app.secret_key = "munt"


# --- Helpers ---

def get_or_set_device_id():
    device_id = request.cookies.get("device_id")
    new_cookie = False
    if not device_id:
        device_id = str(uuid.uuid4())
        new_cookie = True
    return device_id, new_cookie

def ensure_schema():
    """
    Create the per-device table that tests (and the app) rely on.
    The tests seed the master 'flavours' table separately.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flavours_device (
          device_id TEXT NOT NULL,
          flavour   TEXT NOT NULL,
          caffeine  INTEGER NOT NULL,
          size      INTEGER NOT NULL,
          totalDrinks INTEGER NOT NULL DEFAULT 0,
          totalCaffeine INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY (device_id, flavour)
        );
    """)
    conn.commit()
    conn.close()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Routes ---

@app.route("/")
def Home():
    device_id, new_cookie = get_or_set_device_id()

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours_device
        WHERE device_id = ?
        ORDER BY totalDrinks DESC;
    """, (device_id,))
    flavours = cursor.fetchall()
    conn.close()

    total_drinks = sum(row['totalDrinks'] for row in flavours)

    ranks_list = [
        {"name": "Monster",  "drinks": 200},
        {"name": "Diamond",  "drinks": 150},
        {"name": "Platinum", "drinks": 100},
        {"name": "Gold",     "drinks": 70},
        {"name": "Silver",   "drinks": 40},
        {"name": "Bronze",   "drinks": 0},
    ]

    # Determine current rank (list is highest->lowest threshold)
    current_rank = "Bronze"
    for r in ranks_list:
        if total_drinks >= r["drinks"]:
            current_rank = r["name"]
            break

    current_index = next((i for i, r in enumerate(ranks_list) if r["name"] == current_rank), 0)
    next_index = current_index - 1 if current_index > 0 else None

    if next_index is not None:
        next_drinks = ranks_list[next_index]["drinks"]
        drinks_for_next = next_drinks - ranks_list[current_index]["drinks"]
        progress = int(((total_drinks - ranks_list[current_index]["drinks"]) / drinks_for_next) * 100)
    else:
        progress = 100

    image_filename = f"{current_rank.lower()}.png"

    flavour_ranks = []
    for row in flavours:
        drinks = row["totalDrinks"]
        if drinks >= 100:
            rank = "Monster"
        elif drinks >= 50:
            rank = "Diamond"
        elif drinks >= 25:
            rank = "Platinum"
        elif drinks >= 10:
            rank = "Gold"
        elif drinks >= 5:
            rank = "Silver"
        else:
            rank = "Bronze"

        flavour_ranks.append({
            "flavour": row["flavour"],
            "totalDrinks": drinks,
            "totalCaffeine": row["totalCaffeine"],
            "rank": rank,
            "image": f"/static/images/ranks/{rank.lower()}.png",
        })

    resp = make_response(render_template(
        "index.html",
        flavours=flavours,
        current_rank=current_rank,
        progress=progress,
        rank_image=image_filename,
        flavour_ranks=flavour_ranks
    ))
    if new_cookie:
        resp.set_cookie("device_id", device_id, max_age=60*60*24*365*5, httponly=True, samesite="Lax")
    return resp


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        flavour = request.form.get("flavour")
        if not flavour:
            return redirect(url_for("Home"))

        device_id, new_cookie = get_or_set_device_id()
        conn = get_conn()
        cursor = conn.cursor()

        # Update existing row for this device/flavour
        cursor.execute("""
            UPDATE flavours_device
               SET totalDrinks   = totalDrinks + 1,
                   totalCaffeine = totalCaffeine + caffeine
             WHERE device_id = ? AND flavour = ?;
        """, (device_id, flavour))

        if cursor.rowcount == 0:
            # Insert from master flavours table
            cursor.execute("""
                INSERT INTO flavours_device (device_id, flavour, caffeine, size, totalDrinks, totalCaffeine)
                SELECT ?, flavour, caffeine, size, 1, caffeine
                  FROM flavours
                 WHERE flavour = ?;
            """, (device_id, flavour))

        conn.commit()
        conn.close()

        resp = make_response(redirect(url_for("Home")))
        if new_cookie:
            resp.set_cookie("device_id", device_id, max_age=60*60*24*365*5, httponly=True, samesite="Lax")
        return resp

    return render_template("add.html")


@app.route("/stats")
def stats():
    # Color map (trimmed for brevity—keep your full dict if you want)
    flavour_colors = {
        'Absolutely Zero': '#61c5f1',
        'Assault': '#b71c1c',
        'Aussie Style Lemonade': '#f5c72e',
        'Ballers Blend': '#ab2b53',
        'Black': '#000000',
        'Black Ice': '#81aecc',
        'Blue': '#2196f3',
        'Cuba-Libre': '#680106',
        'Cuba-Lima': '#7ecc54',
        'DUB Edition': '#fffaa9',
        'Fury': '#bd2322',
        'Ghost M-100': '#72bd84',
        'Gold': '#ffd700',
        'Green': '#4caf50',
        'Gronk': '#0d57c3',
        'Heavy Metal': '#0d9c32',
        'Import': '#000000',
        'Java Big Black': '#cf8d42',
        'Java Café Latte': '#6e4b36',
        'Java Café Mocha': '#352a29',
        'Java Cold Brew Latte': '#a2492c',
        'Java Cold Brew Sweet Black': '#d1a154',
        'Java Farmers Oats': '#d8cfb9',
        'Java French Vanilla': '#a9955b',
        'Java Irish Blend': '#33b64d',
        'Java Kona Blend': '#5f2f1a',
        'Java Loca Moca': '#986844',
        'Java Mean Bean': '#cbae6c',
        'Java Oatmilk Latte': '#8f595a',
        'Java Oatmilk Mocha': '#b88163',
        'Java Salted Caramel': '#d19848',
        'Java Swiss Chocolate': '#e0dad6',
        'Juiced Aussie Style Lemonade': '#fff176',
        'Juiced Khaotic': '#fabe0e',
        'Juiced Khaotic (Tropical Orange)': "#e0ab0d",
        'Juiced Mango Loco': '#ff9f00',
        'Juiced Monarch': '#fbb13c',
        'Juiced Papillon': '#edc0bf',
        'Juiced Rio Punch': '#fffc15',
        'Khaos': '#f98a40',
        'Lewis Hamilton 44': '#d4af37',
        'Lewis Hamilton Zero Sugar': '#d4af37',
        'Lo-Carb': '#0d47a1',
        'M-80': '#e7e030',
        'MIXXD': '#961e55',
        'Mad Dog': '#71629d',
        'Mango Loco': '#ff9f00',
        'Nitro Anti-Gravity': '#fce02e',
        'Nitro Black Ice': '#1e1e1e',
        'Nitro Cosmic Apple': '#eb0202',
        'Nitro Cosmic Berry': '#c16b82',
        'Nitro Cosmic Berry Lemonade': '#c16b82',
        'Nitro Cosmic Birthday Cake': '#c16b82',
        'Nitro Cosmic Blue Raspberry': '#41a1da',
        'Nitro Cosmic Bubblegum': "#DD12C2",
        'Nitro Cosmic Candy Corn': "#BFE70E",
        'Nitro Cosmic Cherry': "#D81717",
        'Nitro Cosmic Cherry Limeade': "#E95C5C",
        'Nitro Cosmic Citrus': "#9FE72B",
        'Nitro Cosmic Citrus Punch': '#9FE72B',
        'Nitro Cosmic Cotton Candy': "#F324C6",
        'Nitro Cosmic Dragonfruit': "#EC1089",
        'Nitro Cosmic Fruit Punch': "#C02A70",
        'Nitro Cosmic Grape': "#7A0CC4",
        'Nitro Cosmic Kiwi': "#25BB45",
        'Nitro Cosmic Lime': "#1CE937",
        'Nitro Cosmic Lychee': "#E79B9B",
        'Nitro Cosmic Mango': "#FFB445",
        'Nitro Cosmic Marshmallow': "#FFA4A4",
        'Nitro Cosmic Orange': "#F88C10",
        'Nitro Cosmic Passionfruit': "#391946",
        'Nitro Cosmic Peach': "#F0A94D",
        'Nitro Cosmic Pineapple': "#AAB334",
        'Nitro Cosmic Strawberry': "#E23F3F",
        'Nitro Cosmic Tropical Punch': "#A1A030",
        'Nitro Cosmic Watermelon': "#E77777",
        'Nitro Cosmic Yuzu': "#BDC951",
        'Nitro Killer B': "#AFBB44",
        'Nitro Super Dry': "#c0e247",
        'Original': '#2e7d32',
        'Pacific Punch': '#e4572e',
        'Phantom M-100': "#2D7437",
        'Pink': '#ec407a',
        'Pipeline Punch': "#EB3E80",
        'Red': '#f44336',
        'Rehab Green Tea': '#81c784',
        'Rehab Lemonade': '#f4e04d',
        'Rehab Orangeade': '#888888',
        'Rehab Peach Tea': '#f8b195',
        'Rehab Pink Lemonade': "#DF66CA",
        'Rehab Protean': "#FFFFFF",
        'Rehab Rojo Tea': "#B93E3E",
        'Reserve Kiwi Strawberry': "#C75D5D",
        'Reserve Orange Dreamsicle': "#D89736",
        'Reserve Peaches N Crème': "#F3D789",
        'Reserve Watermelon': "#C57878",
        'Reserve White Pineapple': "#F4F5B2",
        'Ripper': "#E6E21D",
        'The Doctor VR46': '#ffd700',
        'Ultra Arctic': "#94ECE8",
        'Ultra Black': "#000000",
        'Ultra Black Cherry': "#4E1919",
        'Ultra Blue': '#4a90e2',
        'Ultra Blue Hawaii': "#7AD8A9",
        'Ultra Chill': "#78B1F1",
        'Ultra Citron': '#ffeb3b',
        'Ultra Cosmic': "#45255A",
        'Ultra Dragonfruit': "#BE2170",
        'Ultra Eclipse': "#5A3A0A",
        'Ultra Fiesta': '#ffa726',
        'Ultra Fiesta Mango': "#C7A547",
        'Ultra Frost': "#6E8792",
        'Ultra Galaxy': "#8B3CA3",
        'Ultra Grape': "#7A22A3",
        'Ultra Green Apple': "#19CA45",
        'Ultra Ice': "#BEF4F8",
        'Ultra Kiwi Lime': "#98E764",
        'Ultra Lemon Ice': "#F3F5A5",
        'Ultra Lychee': "#E792E7",
        'Ultra Moonlight': "#5C5294",
        'Ultra Nova': "#5B14CE",
        'Ultra Paradise': '#66bb6a',
        'Ultra Peachy Keen': '#ffc0cb',
        'Ultra Red': '#c42126',
        'Ultra Rosa': '#f95a9b',
        'Ultra Sakura': "#FC8BF2",
        'Ultra Strawberry Dreams': '#ff99cc',
        'Ultra Sunrise': '#ffa726',
        'Ultra Violet': '#7e57c2',
        'Ultra Violet Storm': "#772FA1",
        'Ultra Watermelon': '#ff5e78',
        'Ultra White Pineapple': "#F5ECA1",
        'Ultra Yuzu': "#C7D63C",
        'Unleaded': '#888888',
        'Mango Loco': '#ff9f00',
        'Gold': '#ffd700',
        'White': '#ffffff',
        'Zero Ultra (white)': '#ffffff',
    }

    device_id, _ = get_or_set_device_id()
    conn = get_conn()
    cursor = conn.cursor()
    # If you want per-device stats, switch to flavours_device + device_id filter
    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours_device
        WHERE device_id = ?
        ORDER BY totalDrinks DESC;
    """, (device_id,))
    rows = cursor.fetchall()
    conn.close()

    total_caffeine = sum(row['totalCaffeine'] for row in rows)
    total_drinks   = sum(row['totalDrinks'] for row in rows)
    total_volume  = sum(500 * row['totalDrinks'] for row in rows)

    pie_data = [{'flavour': row['flavour'], 'totalDrinks': row['totalDrinks']} for row in rows]
    colors = [flavour_colors.get(item['flavour'], '#888888') for item in pie_data]

    return render_template(
        "stats.html",
        flavours=rows,
        total_value=total_caffeine,
        total_drinks=total_drinks,
        stats=pie_data,
        colors=colors,
        total_volume=total_volume,
    )


@app.route("/ranks")
def ranks():
    device_id, _ = get_or_set_device_id()
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flavour, totalDrinks, totalCaffeine
        FROM flavours_device
        WHERE device_id = ?
        ORDER BY totalDrinks DESC;
    """, (device_id,))
    ranked_flavours = cursor.fetchall()
    conn.close()

    total_drinks   = sum(row['totalDrinks']   for row in ranked_flavours)
    total_caffeine = sum(row['totalCaffeine'] for row in ranked_flavours)

    ranks_list = [
        {"name": "Monster",  "drinks": 200},
        {"name": "Diamond",  "drinks": 150},
        {"name": "Platinum", "drinks": 100},
        {"name": "Gold",     "drinks": 70},
        {"name": "Silver",   "drinks": 40},
        {"name": "Bronze",   "drinks": 0},
    ]

    current_rank = "Bronze"
    for r in ranks_list:
        if total_drinks >= r["drinks"]:
            current_rank = r["name"]
            break

    current_index = next((i for i, r in enumerate(ranks_list) if r["name"] == current_rank), 0)
    next_index = current_index - 1 if current_index > 0 else None

    if next_index is not None:
        next_drinks = ranks_list[next_index]["drinks"]
        drinks_for_next = next_drinks - ranks_list[current_index]["drinks"]
        progress = int(((total_drinks - ranks_list[current_index]["drinks"]) / drinks_for_next) * 100)
    else:
        progress = 100

    image_filename = f"{current_rank.lower()}.png"

    flavour_ranks = []
    for row in ranked_flavours:
        drinks = row["totalDrinks"]
        if drinks >= 100:
            rank = "Monster"
        elif drinks >= 50:
            rank = "Diamond"
        elif drinks >= 25:
            rank = "Platinum"
        elif drinks >= 10:
            rank = "Gold"
        elif drinks >= 5:
            rank = "Silver"
        else:
            rank = "Bronze"

        flavour_ranks.append({
            "flavour": row["flavour"],
            "totalDrinks": drinks,
            "totalCaffeine": row["totalCaffeine"],
            "rank": rank,
            "image": f"/static/images/ranks/{rank.lower()}.png",
        })

    return render_template(
        "ranks.html",
        ranks=ranked_flavours,          # <-- make sure ranks.html uses `ranks`
        current_rank=current_rank,
        flavour_ranks=flavour_ranks,
        progress=progress,
        rank_image=image_filename
    )


# Only run the dev server locally, not on PythonAnywhere WSGI import
if __name__ == "__main__":
    app.run(debug=True, port=5000)
