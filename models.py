from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                     #то как выглядит табличка в бд с номерами
    price = Column(Float, nullable=False)
    description = Column(String, default="")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_name = Column(String, nullable=False)                   #то как выглядит табличка со всеми бронями
    date = Column(Date, nullable=False)
    room = relationship("Room")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)                           #то как выглядит табличка с пользователями 67
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)