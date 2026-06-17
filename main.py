from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext
import jwt

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi")

# Parollarni xavfsiz shifrlash va xavfsizlik kaliti
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "RaqamliBozorMaxfiyKaliti"

# ---- MA'LUMOTLAR ANDOZALARI (MODELS) ----
class Elon(BaseModel):
    id: int
    sarlavha: str
    tavsif: str
    narx: float
    valyuta: str = "UZS"
    kategoriya: str
    manzil: str
    telefon: str
    rasm_url: Optional[str] = None
    yaratilgan_vaqt: datetime = datetime.now()

class UserRegister(BaseModel):
    username: str
    password: str
    telefon: str

class UserLogin(BaseModel):
    username: str
    password: str

# ---- VAQTINCHALIK MA'LUMOTLAR BAZASI ----
elonlar_bazasi: List[Elon] = [
    {
        "id": 1,
        "sarlavha": "iPhone 15 Pro Max sotiladi",
        "tavsif": "Holati ideal, 256GB, rangi Natural Titanium.",
        "narx": 12000000,
        "valyuta": "UZS",
        "kategoriya": "Elektronika",
        "manzil": "Toshkent shahar",
        "telefon": "+998901234567",
        "rasm_url": "https://example.com/iphone15.jpg",
        "yaratilgan_vaqt": datetime.now()
    }
]

foydalanuvchilar_bazasi = []

# ---- FOYDALANUVCHILAR TIZIMI (AUTH) ----
@app.post("/register", summary="Yangi foydalanuvchi ro'yxatdan o'tkazish")
def register_user(user: UserRegister):
    for u in foydalanuvchilar_bazasi:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi allaqachon band!")
    
    hashed_password = pwd_context.hash(user.password)
    yangi_user = {
        "username": user.username,
        "password": hashed_password,
        "telefon": user.telefon
    }
    foydalanuvchilar_bazasi.append(yangi_user)
    return {"message": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz! 🥳"}

@app.post("/login", summary="Tizimga kirish va Token olish")
def login_user(user: UserLogin):
    foydalanuvchi = None
    for u in foydalanuvchilar_bazasi:
        if u["username"] == user.username:
            foydalanuvchi = u
            break
            
    if not foydalanuvchi or not pwd_context.verify(user.password, foydalanuvchi["password"]):
        raise HTTPException(status_code=400, detail="Username yoki parol xato!")
    
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "message": "Xush kelibsiz!"}

# ---- E'LONLAR TIZIMI ----
@app.get("/elonlar/", response_model=List[Elon], summary="Barcha e'lonlarni ko'rish")
def barcha_elonlar(kategoriya: Optional[str] = None):
    if kategoriya:
        filtrlangan = [e for e in elonlar_bazasi if e["kategoriya"].lower() == kategoriya.lower()]
        return filtrlangan
    return elonlar_bazasi

@app.post("/elonlar/yaratish/", summary="Yangi e'lon qo'shish")
def elon_yaratish(yangi_elon: Elon):
    elonlar_bazasi.append(yangi_elon.dict())
    return {"message": "E'lon muvaffaqiyatli joylashtirildi!", "elon": yangi_elon}
