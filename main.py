from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "raqmlibozor"
ALGORITHM = "HS256"

# Ma'lumotlar bazasi o'rniga vaqtinchalik ro'yxatlar
users_db = []
elonlar_db = []

class UserRegister(BaseModel):
    username: str
    password: str
    telefon: str

class UserLogin(BaseModel):
    username: str
    password: str

class Elon(BaseModel):
    sarlavha: str
    tavsif: str
    narx: float
    telefon: str

@app.post("/register", summary="Yangi foydalanuvchi ro'yxatdan o'tkazish")
def register_user(user: UserRegister):
    for u in users_db:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi allaqachon mavjud")
    
    # Parolni faqat bitta marta xeshlaymiz
    hashed_password = pwd_context.hash(user.password)
    
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
    for u in users_db:
        if u["username"] == user.username:
            db_user = u
            break
            
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi yoki parol xato")
        
    expire = datetime.utcnow() + timedelta(hours=24)
    token_data = {"sub": user.username, "exp": expire}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/elonlar/", summary="Barcha e'lonlarni ko'rish")
def get_elonlar():
    return elonlar_db

@app.post("/elonlar/yaratish/", summary="Yangi e'lon qo'shish")
def create_elon(elon: Elon):
    elonlar_db.append(elon.dict())
    return {"message": "E'loningiz muvaffaqiyatli qo'shildi! ✨", "elon": elon}
