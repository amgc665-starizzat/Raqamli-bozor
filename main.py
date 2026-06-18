from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Any

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "raqmlibozor"
ALGORITHM = "HS256"

# Ma'lumotlar bazasi o'rniga vaqtinchalik ro'yxatlar
users_db = []
elonlar_db = []

# MUTLAQ ERKIN MODELLAR (Har qanday turni injiqliksiz qabul qiladi)
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
    # Agar foydalanuvchi nomi matn bo'lsa, uni bazadan tekshirish
    if user.username:
        for u in users_db:
            if str(u["username"]).strip().lower() == str(user.username).strip().lower():
                raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi allaqachon mavjud")
    
    # Parolni xavfsiz matnga o'girib, keyin xeshlaymiz (injiqlik qilmasligi uchun)
    plain_password = str(user.password) if user.password is not None else "12345"
    hashed_password = pwd_context.hash(plain_password)
    
    new_user = {
        "username": user.username,
        "password": hashed_password,
        "telefon": user.telefon
    }
    users_db.append(new_user)
    return {"message": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz! 🥳"}

@app.post("/login", summary="Tizimga kirish va Token olish")
def login_user(user: UserLogin):
    db_user = None
    input_username = str(user.username).strip().lower() if user.username is not None else ""
    
    for u in users_db:
        if u["username"] and str(u["username"]).strip().lower() == input_username:
            db_user = u
            break
            
    plain_password = str(user.password) if user.password is not None else ""
    
    if not db_user or not pwd_context.verify(plain_password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi yoki parol xato")
        
    expire = datetime.utcnow() + timedelta(hours=24)
    token_data = {"sub": str(user.username), "exp": expire}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/elonlar/", summary="Barcha e'lonlarni ko'rish")
def get_elonlar():
    return elonlar_db

@app.post("/elonlar/yaratish/", summary="Yangi e'lon qo'shish")
def create_elon(elon: Elon):
    elonlar_db.append(elon.dict())
    return {"message": "E'loningiz muvaffaqiyatli qo'shildi! ✨", "elon": elon}
