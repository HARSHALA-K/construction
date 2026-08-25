import os
import sqlite3
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Local Construction Price API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "prices_demo.db")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def init_db():
    """Sets up database structure and correctly checks for empty states."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS material_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layout TEXT,
                city TEXT,
                material TEXT,
                grade TEXT,
                price TEXT
            )
        ''')
        conn.commit()

        cursor.execute("PRAGMA table_info(material_prices)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        if "layout" not in existing_columns:
            try:
                cursor.execute("ALTER TABLE material_prices ADD COLUMN layout TEXT")
                conn.commit()
            except sqlite3.OperationalError as exc:
                if "duplicate column name" in str(exc).lower():
                    pass
                else:
                    raise

        # FIXED: Extracting index [0] to safely count rows
        cursor.execute("SELECT COUNT(*) FROM material_prices")
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            print("Database is empty. Seeding starter data for the demo...")
            seed_fallback_data(conn)

def seed_fallback_data(conn):
    """Injects layout and granular material categories across demo cities."""
    fallback_items = [
        # Mumbai Dataset
        ("", "Mumbai", "Cement", "OPC 53 Grade (UltraTech)", "₹410–450 / bag"),
        ("", "Mumbai", "Steel / TMT Bars", "Fe500 Premium", "₹68–76 / kg"),
        ("", "Mumbai", "Red Bricks", "Clay Kiln Baked", "₹8,500–11,000 / 1000 pcs"),
        ("", "Mumbai", "River Sand", "Fine Premium Grade", "₹65–85 / cft"),
        ("", "Mumbai", "Floor Tiles", "Vitrified Double-Charge", "₹55–90 / sqft"),
        ("", "Mumbai", "Exterior Paint", "Emulsion Premium", "₹120–200 / L"),
        ("", "Mumbai", "Electrical", "Wiring & Switches", "Standard Box Rate"),
        ("", "Mumbai", "Plumbing", "Pipes & Sanitary Fittings", "Standard Unit Rate"),
        
        # Bengaluru Dataset
        ("", "Bengaluru", "Cement", "OPC 53 Grade (Ramco)", "₹370–420 / bag"),
        ("", "Bengaluru", "Steel / TMT Bars", "Fe500 Standard", "₹60–72 / kg"),
        ("", "Bengaluru", "Red Bricks", "Wire-cut / Local Clay", "₹6,500–9,000 / 1000 pcs"),
        ("", "Bengaluru", "River Sand", "M-Sand Premium alternative", "₹45–70 / cft"),
        ("", "Bengaluru", "Floor Tiles", "Ceramic and Floor Tiles", "₹40–75 / sqft"),
        ("", "Bengaluru", "Exterior Paint", "Emulsion & Primer Mix", "₹100–160 / L"),
        ("", "Bengaluru", "Electrical", "Wiring, Switches & Fittings", "Standard Box Rate"),
        ("", "Bengaluru", "Plumbing", "Pipes, Fittings & Sanitary", "Standard Unit Rate"),
        
        # Noida Dataset
        ("", "Noida", "Cement", "OPC 53 Grade (Ambuja)", "₹390–430 / bag"),
        ("", "Noida", "Steel / TMT Bars", "Fe500 Grade", "₹64–74 / kg"),
        ("", "Noida", "Red Bricks", "Fly-Ash & Clay Mix", "₹7,000–9,500 / 1000 pcs"),
        ("", "Noida", "River Sand", "Yamuna Basin Source", "₹55–75 / cft"),
        ("", "Noida", "Floor Tiles", "Standard Glazed Vitrified", "₹45–80 / sqft"),
        ("", "Noida", "Exterior Paint", "Weather-proof Emulsion", "₹110–180 / L"),
        ("", "Noida", "Electrical", "Wiring, Switches & Fittings", "Standard Box Rate"),
        ("", "Noida", "Plumbing", "Pipes, Fittings & Sanitary", "Standard Unit Rate"),

        ("", "Mumbai", "Cement", "OPC 53 Grade (UltraTech)", "₹435/bag"),
        ("", "Delhi NCR", "TMT Bar", "12mm (Fe 550D)", "₹64,500/ton"),
        ("", "Bengaluru", "Aggregates", "20mm Blue Metal", "₹3,400/brass"),
        ("", "Chennai", "River Sand", "Standard Quality", "₹2,950/tonne"),
        ("", "Hyderabad", "Bricks", "Red Clay (9x4x3)", "₹9/piece"),
        ("", "Pune", "Ready Mix Concrete", "M25 Grade", "₹4,200/cum"),
    ]
    cursor = conn.cursor()
    # FIXED: Realigned query map parameters to fill all 5 content fields safely
    cursor.executemany(
        "INSERT INTO material_prices (layout, city, material, grade, price) VALUES (?, ?, ?, ?, ?)", 
        fallback_items
    )
    conn.commit()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/refresh")
def refresh_prices_from_web():

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM material_prices")
        seed_fallback_data(conn)
        return {
        "status": "success",
        "source": "local_demo_seeder",
        "message": "Database wiped and re-seeded successfully with Mumbai, Bengaluru, and Noida items."
    }

@app.get("/api/prices")
def get_database_prices(city: str = None):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if city:
            cursor.execute(
                "SELECT id, layout, city, material, grade, price FROM material_prices WHERE LOWER(city) = LOWER(?)", 
                (city,)
            )
        else:
            cursor.execute("SELECT id, layout, city, material, grade, price FROM material_prices")
            
        rows = cursor.fetchall()
        
    return {"status": "success", "data": [dict(row) for row in rows]}

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Construction Price API is operational. Hit /api/refresh then verify via /api/prices?city=mumbai"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
