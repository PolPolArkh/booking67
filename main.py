import sqlite3

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def init_db():
    conn = sqlite3.connect("hotel.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER,
        guest TEXT,
        date TEXT
    )""")
    if conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
        conn.executemany("INSERT INTO rooms (name, price) VALUES (?, ?)", [
            ("Стандарт", 3000),
            ("Люкс", 8000),
        ])
        conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    conn = sqlite3.connect("hotel.db")
    rooms = conn.execute("SELECT * FROM rooms").fetchall()
    bookings = conn.execute("""
        SELECT bookings.id, rooms.name, guest, date
        FROM bookings JOIN rooms ON rooms.id = bookings.room_id
    """).fetchall()
    conn.close()
    return templates.TemplateResponse(request, "index.html", {
    "rooms": rooms, "bookings": bookings
})

@app.post("/book")
def book(room_id: int = Form(...), guest: str = Form(...), date: str = Form(...)):
    conn = sqlite3.connect("hotel.db")
    conn.execute("INSERT INTO bookings (room_id, guest, date) VALUES (?, ?, ?)",
                 (room_id, guest, date))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/cancel/{booking_id}")
def cancel(booking_id: int):
    conn = sqlite3.connect("hotel.db")
    conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
