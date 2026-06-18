from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any
import json
import os

app = FastAPI(title="Raqamli Bozor API", description="E'lonlar va foydalanuvchilar platformasi")

# ---- BILANMA-KETIN MA'LUMOTLAR BAZASI (FAYLDA SAQLASH) ----
USERS_FILE = "users_db.json"
ELONLAR_FILE = "elonlar_db.json"

def load_data(filename, default_value):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_value
    return default_value

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Ma'lumotlarni yuklab olish
users_db = load_data(USERS_FILE, [])
elonlar_db = load_data(ELONLAR_FILE, [
    {"sarlavha": "Chevrolet Gentra", "tavsif": "Yili 2023, holati a'lo, rangi oq", "narx": "13500", "telefon": "+998991234567"},
    {"sarlavha": "iPhone 15 Pro", "tavsif": "128GB, rangi Natural Titanium, yangi", "narx": "950", "telefon": "+998907654321"}
])

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

@app.get("/", response_class=HTMLResponse, summary="Asosiy vizual sahifa")
def home_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raqamli Bozor - Platforma</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
            body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; flex-direction: column; }
            .container { background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .main-page { background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); width: 100%; max-width: 800px; display: none; }
            h2, h3 { text-align: center; color: #333; margin-bottom: 24px; }
            .input-group { margin-bottom: 16px; position: relative; }
            .input-group label { display: block; margin-bottom: 6px; color: #666; font-size: 14px; font-weight: 500; }
            .input-group input, .input-group textarea { width: 100%; padding: 12px 16px; border: 1px solid #cccccc; border-radius: 8px; font-size: 15px; outline: none; }
            .input-group input:focus { border-color: #007bff; }
            
            .password-wrapper { position: relative; display: flex; align-items: center; }
            .password-wrapper input { padding-right: 45px; }
            .toggle-password { position: absolute; right: 15px; cursor: pointer; user-select: none; font-size: 18px; color: #666; }
            
            button { width: 100%; padding: 12px; background: #007bff; border: none; border-radius: 8px; color: white; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; }
            button:hover { background: #0056b3; }
            .logout-btn { background: #dc3545; padding: 6px 12px; font-size: 14px; width: auto; margin-top: 0; }
            .logout-btn:hover { background: #c82333; }
            
            .message { margin-top: 15px; padding: 12px; border-radius: 8px; font-size: 14px; text-align: center; display: none; }
            .success { background: #d4edda; color: #155724; display: block; }
            .error { background: #f8d7da; color: #721c24; display: block; }
            .toggle-link { text-align: center; margin-top: 20px; font-size: 14px; color: #007bff; cursor: pointer; text-decoration: underline; }
            
            .navbar { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px; }
            .elon-card { background: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
            .elon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            @media (max-width: 600px) { .elon-grid { grid-template-columns: 1fr; } }
            .price { font-weight: bold; color: #28a745; font-size: 18px; margin-top: 10px; }
        </style>
    </head>
    <body>

    <!-- 1. KIRISH VA RO'YXATDAN O'TISH OYNASI -->
    <div class="container" id="authBox">
        <h2 id="formTitle">Ro'yxatdan O'tish</h2>
        
        <div class="input-group">
            <label>Foydalanuvchi nomi</label>
            <input type="text" id="username" placeholder="Masalan: qodirjon">
        </div>
        
        <div class="input-group">
            <label>Parol</label>
            <div class="password-wrapper">
                <input type="password" id="password" placeholder="Parolingizni kiriting">
                <span class="toggle-password" onclick="togglePasswordVisibility()">👁️</span>
            </div>
        </div>
        
        <div class="input-group" id="phoneGroup">
            <label>Telefon raqam</label>
            <input type="text" id="telefon" placeholder="+998997113702">
        </div>

        <button onclick="handleAuth()">Yuborish</button>
        <div id="msgBox" class="message"></div>
        <div class="toggle-link" id="toggleLink" onclick="toggleForm()">Sizda allaqachon profil bormi? Kirish</div>
    </div>

    <!-- 2. ICHKARIDAGI ASOSIY BOZOR SAHIFASI -->
    <div class="main-page" id="marketPage">
        <div class="navbar">
            <h3>🚀 Raqamli Bozor Platformasi</h3>
            <div style="display: flex; align-items: center; gap: 15px;">
                <div>Salom, <span id="userDisplay" style="font-weight:bold; color:#007bff;"></span>!</div>
                <!-- Akkauntdan chiqish tugmasi -->
                <button class="logout-btn" onclick="logout()">Chiqish 🚪</button>
            </div>
        </div>

        <div class="elon-grid">
            <div>
                <h4>Yangi e'lon joylashtirish</h4>
                <div class="input-group" style="margin-top:15px;">
                    <label>E'lon sarlavhasi</label>
                    <input type="text" id="elonSarlavha" placeholder="Masalan: Spark sotiladi">
                </div>
                <div class="input-group">
                    <label>Tavsif (Batafsil ma'lumot)</label>
                    <textarea id="elonTavsif" rows="3" placeholder="Holati, yili, yurgani haqida..."></textarea>
                </div>
                <div class="input-group">
                    <label>Narxi ($ yoki So'm)</label>
                    <input type="text" id="elonNarx" placeholder="Masalan: 7000">
                </div>
                <div class="input-group">
                    <label>Aloqa uchun telefon</label>
                    <input type="text" id="elonTel" placeholder="+998997113702">
                </div>
                <button onclick="addElon()" style="background:#28a745;">E'lonni joylash ✨</button>
                <div id="elonMsg" class="message"></div>
            </div>

            <div>
                <h4>Barcha faol e'lonlar</h4>
                <div id="elonlarRoʻyxati" style="margin-top:15px; max-height:450px; overflow-y:auto;"></div>
            </div>
        </div>
    </div>

    <script>
        let isRegisterMode = true;

        // --- AKKAUNTNI ESDAN CHIQARMAYDIGAN QILISH (AVTO-LOGIN) ---
        window.onload = function() {
            const savedUser = localStorage.getItem('activeUser');
            if (savedUser) {
                // Agar foydalanuvchi avval kirgan bo'lsa, to'g'ridan-to'g'ri ichkariga o'tkazish
                document.getElementById('authBox').style.display = 'none';
                document.getElementById('marketPage').style.display = 'block';
                document.getElementById('userDisplay').innerText = savedUser;
                loadElonlar();
            }
        }

        function togglePasswordVisibility() {
            const passwordInput = document.getElementById('password');
            const toggleIcon = document.querySelector('.toggle-password');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.innerText = '🙈';
            } else {
                passwordInput.type = 'password';
                toggleIcon.innerText = '👁️';
            }
        }

        function toggleForm() {
            isRegisterMode = !isRegisterMode;
            const title = document.getElementById('formTitle');
            const phoneGroup = document.getElementById('phoneGroup');
            const toggleLink = document.getElementById('toggleLink');
            document.getElementById('msgBox').style.display = 'none';

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
            const bodyData = isRegisterMode ? { username, password, telefon } : { username, password };

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });
                const result = await response.json();

                if (response.ok) {
                    msgBox.innerText = result.message;
                    msgBox.classList.add('success');
                    
                    // Brauzer xotirasiga foydalanuvchini yozib qo'yamiz (Akkauntdan chiqib ketmaydi)
                    localStorage.setItem('activeUser', username);
                    
                    setTimeout(() => {
                        document.getElementById('authBox').style.display = 'none';
                        document.getElementById('marketPage').style.display = 'block';
                        document.getElementById('userDisplay').innerText = username;
                        loadElonlar();
                    }, 1000);
                } else {
                    msgBox.innerText = result.detail || "Xatolik!";
                    msgBox.classList.add('error');
                }
            } catch (err) {
                msgBox.innerText = "Server xatosi!";
                msgBox.classList.add('error');
            }
        }

        // AKKAUNTDAN CHIQISH FUNKSIYASI
        function logout() {
            localStorage.removeItem('activeUser'); // Xotirani tozalash
            document.getElementById('marketPage').style.display = 'none';
            document.getElementById('authBox').style.display = 'block';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            document.getElementById('msgBox').style.display = 'none';
        }

        async function loadElonlar() {
            const res = await fetch('/elonlar/');
            const elonlar = await res.json();
            const box = document.getElementById('elonlarRoʻyxati');
            box.innerHTML = '';
            
            elonlar.reverse().forEach(e => {
                box.innerHTML += `
                    <div class="elon-card">
                        <h5 style="font-size:16px; color:#333;">${e.sarlavha}</h5>
                        <p style="font-size:14px; color:#666; margin: 5px 0;">${e.tavsif}</p>
                        <div style="font-size:13px; color:#999;">📞 Tel: ${e.telefon}</div>
                        <div class="price">${e.narx}</div>
                    </div>
                `;
            });
        }

        async function addElon() {
            const sarlavha = document.getElementById('elonSarlavha').value;
            const tavsif = document.getElementById('elonTavsif').value;
            const narx = document.getElementById('elonNarx').value;
            const telefon = document.getElementById('elonTel').value;
            const elonMsg = document.getElementById('elonMsg');

            const response = await fetch('/elonlar/yaratish/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sarlavha, tavsif, narx, telefon })
            });

            if (response.ok) {
                elonMsg.innerText = "E'lon muvaffaqiyatli qo'shildi!";
                elonMsg.className = "message success";
                document.getElementById('elonSarlavha').value = '';
                document.getElementById('elonTavsif').value = '';
                document.getElementById('elonNarx').value = '';
                loadElonlar();
            } else {
                elonMsg.innerText = "Xato!";
                elonMsg.className = "message error";
            }
        }
    </script>
    </body>
    </html>
    """
    return html_content

@app.post("/register")
def register_user(user: UserRegister):
    username_str = str(user.username).strip() if user.username is not None else ""
    if not username_str:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomini yozing!")
    for u in users_db:
        if str(u["username"]).strip().lower() == username_str.lower():
            raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi band!")
    
    users_db.append({"username": user.username, "password": str(user.password), "telefon": user.telefon})
    save_data(USERS_FILE, users_db) # Faylga saqlash
    return {"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz! 🎉"}

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
        raise HTTPException(status_code=400, detail="Login yoki parol xato!")
    return {"message": "Tizimga muvaffaqiyatli kirdingiz! 🔓"}

@app.get("/elonlar/")
def get_elonlar():
    return elonlar_db

@app.post("/elonlar/yaratish/")
def create_elon(elon: Elon):
    elonlar_db.append(elon.dict())
    save_data(ELONLAR_FILE, elonlar_db) # Faylga saqlash
    return {"message": "Qo'shildi", "elon": elon}
