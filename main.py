from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi")

# Ma'lumotlar bazasi o'rniga vaqtinchalik ro'yxatlar
users_db = []
elonlar_db = []

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

# ---- CHIROYLI FRONTEND SAHIFASI ----
@app.get("/", response_class=HTMLResponse, summary="Asosiy vizual sahifa")
def home_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raqamli Bozor - Kirish va Ro'yxatdan o'tish</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
            .container { background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            h2 { text-align: center; color: #333; margin-bottom: 24px; font-weight: 600; }
            .input-group { margin-bottom: 16px; }
            .input-group label { display: block; margin-bottom: 6px; color: #666; font-size: 14px; font-weight: 500; }
            .input-group input { width: 100%; padding: 12px 16px; border: 1px solid #cccccc; border-radius: 8px; font-size: 15px; transition: border-color 0.2s; outline: none; }
            .input-group input:focus { border-color: #007bff; }
            button { width: 100%; padding: 12px; background: #007bff; border: none; border-radius: 8px; color: white; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; margin-top: 10px; }
            button:hover { background: #0056b3; }
            .message { margin-top: 15px; padding: 12px; border-radius: 8px; font-size: 14px; text-align: center; display: none; }
            .success { background: #d4edda; color: #155724; display: block; }
            .error { background: #f8d7da; color: #721c24; display: block; }
            .toggle-link { text-align: center; margin-top: 20px; font-size: 14px; color: #007bff; cursor: pointer; text-decoration: underline; }
        </style>
    </head>
    <body>

    <div class="container" id="authBox">
        <h2 id="formTitle">Ro'yxatdan O'tish</h2>
        
        <div class="input-group">
            <label for="username">Foydalanuvchi nomi (Username)</label>
            <input type="text" id="username" placeholder="Masalan: qodirjon">
        </div>
        
        <div class="input-group">
            <label for="password">Parol</label>
            <input type="password" id="password" placeholder="Parolingizni kiriting">
        </div>
        
        <div class="input-group" id="phoneGroup">
            <label for="telefon">Telefon raqam</label>
            <input type="text" id="telefon" placeholder="Masalan: +998997113702">
        </div>

        <button id="submitBtn" onclick="handleAuth()">Yuborish</button>
        
        <div id="msgBox" class="message"></div>
        
        <div class="toggle-link" id="toggleLink" onclick="toggleForm()">Sizda allaqachon profil bormi? Kirish</div>
    </div>

    <script>
        let isRegisterMode = true;

        function toggleForm() {
            isRegisterMode = !isRegisterMode;
            const title = document.getElementById('formTitle');
            const phoneGroup = document.getElementById('phoneGroup');
            const toggleLink = document.getElementById('toggleLink');
            const msgBox = document.getElementById('msgBox');
            msgBox.style.display = 'none';

            if (isRegisterMode) {
                title.innerText = "Ro'yxatdan O'tish";
                phoneGroup.style.display = "block";
                toggleLink.innerText = "Sizda allaqachon profil bormi? Kirish";
            } else {
                title.innerText = "Tizimga Kirish";
                phoneGroup.style.display = "none";
                toggleLink.innerText = "Yangi profil yaratish (Ro'yxatdan o'tish)";
            }
        }

        async function handleAuth() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const telefon = document.getElementById('telefon').value;
            const msgBox = document.getElementById('msgBox');
            
            msgBox.style.display = 'none';
            msgBox.className = "message";

            const url = isRegisterMode ? '/register' : '/login';
            const bodyData = isRegisterMode 
                ? { username, password, telefon } 
                : { username, password };

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });

                const result = await response.json();

                if (response.ok) {
                    msgBox.innerText = result.message || "Muvaffaqiyatli!";
                    msgBox.classList.add('success');
                } else {
                    msgBox.innerText = result.detail || "Xatolik yuz berdi";
                    msgBox.classList.add('error');
                }
            } catch (err) {
                msgBox.innerText = "Serverga ulanishda xato!";
                msgBox.classList.add('error');
            }
        }
    </script>
    </body>
    </html>
    """
    return html_content

# ---- BACKEND ENDPOINTLARI ----
@app.post("/register")
def register_user(user: UserRegister):
    username_str = str(user.username).strip() if user.username is not None else ""
    if not username_str:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomini yozing!")
        
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

@app.post("/login")
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
        
    return {"message": f"Xush kelibsiz, {user.username}! Tizimga muvaffaqiyatli kirdingiz! 🔓"}

@app.get("/elonlar/")
def get_elonlar():
    return elonlar_db

@app.post("/elonlar/yaratish/")
def create_elon(elon: Elon):
    elonlar_db.append(elon.dict())
    return {"message": "E'loningiz qo'shildi! ✨", "elon": elon}
