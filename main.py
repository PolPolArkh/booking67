from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
def update_db_structure():
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT description FROM rooms LIMIT 1"))
        except Exception:  
            print("Добавляем колонку description в таблицу rooms...")
            conn.execute(text("ALTER TABLE rooms ADD COLUMN description TEXT DEFAULT ''"))
            conn.commit()

update_db_structure()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def seed_rooms():
    db = next(get_db())
    if db.query(models.Room).count() == 0:
        rooms = [
            models.Room(name="Стандарт", price=9000, description="Уютный номер с одной кроватью"),
            models.Room(name="Стандарт Твин", price=10200, description="Две односпальные кровати"),
            models.Room(name="Полулюкс", price=15500, description="Просторный номер с зоной отдыха"),  #короче, записываем в бд виды номеров
            models.Room(name="Люкс", price=20000, description="Большой номер с панорамным видом"),
            models.Room(name="Президентский", price=45000, description="Двухкомнатный номер с джакузи"),
        ]
        db.add_all(rooms)
        db.commit()
    db.close()

seed_rooms()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")
    if email:
        return db.query(models.Customer).filter(models.Customer.email == email).first()
    return None

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), user: models.Customer = Depends(get_current_user)):  
    if not user:                                         
        return RedirectResponse("/login", status_code=303)
                                                           # тут закидывает на главную страницу и идёт проверка, зареган чел или нет
    rooms = db.query(models.Room).all()
    bookings = db.query(models.Booking).all()
    
    return templates.TemplateResponse(request=request, name="index.html", context={
        "rooms": rooms, "bookings": bookings, "username": user.full_name
    })

@app.get("/register")
def register_page(request: Request):                                             #показ страницы регистрации
    return templates.TemplateResponse(request=request, name="register.html")  

@app.post("/register")
def register_user(
    full_name: str = Form(...),    
    phone: str = Form(...), 
    email: str = Form(...),                             #тут короче заполнение полей регистрации
    password: str = Form(...),
    db: Session = Depends(get_db), 
    request: Request = None
):
    if db.query(models.Customer).filter(models.Customer.email == email).first():
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Этот Email уже занят"})  #тут выводится ошибка если почта заеята 
    
    db.add(models.Customer(full_name=full_name, phone=phone, email=email, password=password))
    db.commit()
    
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login_user(
    email: str = Form(...),                       #снова заполнение полей, только уже для входа 
    password: str = Form(...),
    db: Session = Depends(get_db), 
    request: Request = None
):
    user = db.query(models.Customer).filter(models.Customer.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Неверный email или пароль"})  #ошибка при входе в аккаунт
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@app.get("/logout")
def logout_user():
    response = RedirectResponse("/login", status_code=303)         #выход из аккаунта
    response.delete_cookie("user_email", path="/")
    return response

@app.post("/book")
def book_room(
    room_id: int = Form(...), 
    guest: str = Form(...),                               #поляя для брони 
    date: str = Form(...),
    db: Session = Depends(get_db),
    user: models.Customer = Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    check_in = datetime.strptime(date, "%Y-%m-%d").date()
    check_out = check_in + timedelta(days=1)                     
    existing = db.query(models.Booking).filter(
        models.Booking.room_id == room_id,                     #проверка на занятость даты на бронб
        models.Booking.date < check_out,
        models.Booking.date >= check_in
    ).first()
    if existing:
        return RedirectResponse("/?error=room_busy", status_code=303)
    db.add(models.Booking(room_id=room_id, guest_name=guest, date=check_in))      
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/cancel/{booking_id}")
def cancel_booking(
    booking_id: int, 
    db: Session = Depends(get_db),
    user: models.Customer = Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()      #тут отмена брони
    if booking:
        db.delete(booking)
        db.commit()
    return RedirectResponse("/", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)     #67