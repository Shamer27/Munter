import sqlite3
import uuid
from flask import Flask, render_template, make_response, request, redirect, url_for
from flask_compress import Compress
import matplotlib
matplotlib.use('Agg')  # safe on servers without display

# --- Config ---
DB_PATH = "./.database/flavors.db"   # <-- adjust if your DB is elsewhere

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
        'Original': '#2e7d32',
        'Ultra Blue': '#4a90e2',
        'Ultra Paradise': '#66bb6a',
        'Ultra Red': '#c42126',
        'Ultra Violet': '#7e57c2',
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
