import sqlite3
import main


def _fetch_device_rows(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM flavours_device").fetchall()
    conn.close()
    return rows


def test_home_sets_cookie_and_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200

    # A new device_id cookie should be set on first visit
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "device_id=" in set_cookie or client.cookie_jar._cookies  # depending on Werkzeug version

    # Page should render something recognizable (adjust to your template)
    assert b"Flavour" in resp.data or b"Add A Drink" in resp.data


def test_add_increments_totals(client):
    # First visit to initialize rows for this device
    client.get("/")

    # Post a flavour from the master table
    flavour = "Ultra Rosa"
    resp = client.post("/add", data={"flavour": flavour}, follow_redirects=True)
    assert resp.status_code == 200  # redirected to home

    # Check DB values
    rows = _fetch_device_rows(main.DB_PATH)
    # Expect exactly one row for Ultra Rosa
    ultra_rosa_rows = [r for r in rows if r["flavour"] == flavour]
    assert len(ultra_rosa_rows) == 1
    r = ultra_rosa_rows[0]
    assert r["totalDrinks"] == 1
    assert r["totalCaffeine"] == r["caffeine"] * 1

    # Post again to ensure increment logic works
    resp = client.post("/add", data={"flavour": flavour}, follow_redirects=True)
    assert resp.status_code == 200

    rows = _fetch_device_rows(main.DB_PATH)
    ultra_rosa_rows = [r for r in rows if r["flavour"] == flavour]
    r = ultra_rosa_rows[0]
    assert r["totalDrinks"] == 2
    assert r["totalCaffeine"] == r["caffeine"] * 2


def test_stats_page_renders(client):
    # Seed some drinks
    client.get("/")
    client.post("/add", data={"flavour": "Ultra Rosa"})
    client.post("/add", data={"flavour": "Ultra Red"})

    resp = client.get("/stats")
    assert resp.status_code == 200
    # Should contain table headings or labels from your template
    assert b"Flavour Statistics" in resp.data or b"Drink Distribution" in resp.data


def test_ranks_page_and_current_rank(client):
    # Seed drinks to reach Silver (>= 5 total drinks in your thresholds)
    client.get("/")
    for _ in range(5):
        client.post("/add", data={"flavour": "Ultra Rosa"})

    resp = client.get("/ranks")
    assert resp.status_code == 200

    # Your template displays "Your Current Rank: Silver" when >=5 drinks
    assert b"Your Current Rank" in resp.data
    assert b"Silver" in resp.data

    # And the image file name should appear in the HTML
    # (e.g., <img src="/static/images/ranks/silver.png" ...)
    assert b"silver.png" in resp.data
