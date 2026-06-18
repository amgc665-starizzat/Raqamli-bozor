from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi (Injiqliksiz Versiya)")

# Ma'lumotlar bazasi o'rniga vaqtinchalik ro'yxatlar
users_db = []
elonlar_db = []

# MUTLAQ ERKIN MODELLAR (Har qanday narsani boricha bag'riga bosadi)
class UserRegister(BaseModel):
    username: Any = None
    password: Any = None
    telefon: Any = None

class UserLogin(BaseModel):
    username: Any = None
    password: Any = None

class Elon(BaseModel):
    sarlavha: Any = None
    tavsif: Any = None
    narx: Any = None
    telefon: Any = None

@app.post("/register", summary="Yangi foydalanuvchi ro'yxatdan o'tkazish")
def register_user(user: UserRegister):
    # Bo'sh bo'lsa ham, har qanday belgini ham qabul qiladi
    username_str = str(user.username).strip() if user.username is not None else "user"
    
    for u in users_db:
        if str(u["username"]).strip().lower() == username_str.lower():
            raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi allaqachon mavjud")
    
    new_user = {
        "username": user.username,
        "password": str(user.password),
        "telefon": user.telefon
    }
    users_db.append(new_user)
    return {"message": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz! 🥳"}

@app.post("/login", summary="Tizimga kirish")
def login_user(user: UserLogin):
    input_username = str(user.username).strip().lower() if user.username is not None else ""
    input_password = str(user.password) if user.password is not None else ""
    
    db_user = None
    for u in users_db:
        if str(u["username"]).strip().lower() == input_username:
            db_user = u
            break
            
    if not db_user or str(db_user["password"]) != input_password:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi yoki parol xato")
        
    return {"message": "Tizimga muvaffaqiyatli kirdingiz! 🔓", "username": user.username}

@app.get("/elonlar/", summary="Barcha e'lonlarni ko'rish")
def get_elonlar():
    return elonlar_db

@app.post("/elonlar/yaratish/", summary="Yangi e'lon qo'shish")
def create_elon(elon: Elon):
    elonlar_db.append(elon.dict())
    return {"message": "E'loningiz muvaffaqiyatli qo'shildi! ✨", "elon": elon}
