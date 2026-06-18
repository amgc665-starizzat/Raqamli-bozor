from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any
from pymongo import MongoClient
import os

app = FastAPI(title="Raqamli Bozor API")

# ---- ENG XAVFSIZ ULASH USULI ----
MONGO_URL = "mongodb+srv://izzat:izzat2008@cluster0.o3bsglh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client["raqamli_bozor_db"]
    users_collection = db["users"]
    elonlar_collection = db["elonlar"]
    # Ulanishni sinab ko'rish
    client.admin.command('ping')
except Exception as e:
    print(f"Baza bilan ulanishda xato: {e}")

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

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raqamli Bozor</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
            body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; flex-direction: column; }
            .container { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .main-page { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 600px; display: none; }
            .input-group { margin-bottom: 12px; }
            .input-group label { display: block; margin-bottom: 4px; color: #555; font-size: 14px; }
            .input-group input, .input-group textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; }
            button { width: 100%; padding: 10px; background: #007bff; border: none; border-radius: 6px; color: white; font-size: 16px; cursor: pointer; }
            .message { margin-top: 10px; padding: 10px; border-radius: 6px; font-size: 14px; text-align: center; display: none; }
            .success { background: #d4edda; color: #155724; display: block; }
            .error { background: #f8d7da; color: #721c24; display: block; }
            .elon-card { background: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
        </style>
    </head>
    <body>

    <div class="container" id="authBox">
        <h2 id="formTitle" style="text-align:center; margin-bottom:15px;">Ro'yxatdan O'tish</h2>
        <div class="input-group">
            <label>Foydalanuvchi nomi</label>
            <input type="text" id="username">
        </div>
        <div class="input-group">
            <label>Parol</label>
            <input type="password" id="password">
        </div>
        <div class="input-group" id="phoneGroup">
            <label>Telefon raqam</label>
            <input type="text" id="telefon">
        </div>
        <button onclick="handleAuth()">Yuborish</button>
        <div id="msgBox" class="message"></div>
        <p id="toggleLink" onclick="toggleForm()" style="text-align:center; margin-top:15px; color:#007bff; cursor:pointer; font-size:14px;">Kirish rejimiga o'tish</p>
    </div>

    <div class="main-page" id="marketPage">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px; align-items:center;">
            <h3>Raqamli Bozor</h3>
            <button onclick="logout()" style="width:auto; background:#dc3545; padding:5px 10px;">Chiqish</button>
        </div>
        
        <div class="input-group">
            <input type="text" id="elonSarlavha" placeholder="E'lon sarlavhasi">
        </div>
        <div class="input-group">
            <textarea id="elonTavsif" placeholder="Tavsif"></textarea>
        </div>
        <div class="input-group">
            <input type="text" id="elonNarx" placeholder="Narxi">
        </div>
        <div class="input-group">
            <input type="text" id="elonTel" placeholder="Telefon raqam">
        </div>
        <button onclick="addElon()" style="background:#28a745;">E'lon joylash</button>
        <div id="elonMsg" class="message"></div>

        <h4 style="margin-top:20px; margin-bottom:10px;">E'lonlar ro'yxati:</h4>
        <div id="elonlarRoʻyxati"></div>
    </div>

    <script>
        let isRegisterMode = true;

        window.onload = function() {
            if (localStorage.getItem('activeUser')) {
                showMarket();
            }
        }

        function toggleForm() {
            isRegisterMode = !isRegisterMode;
            document.getElementById('formTitle').innerText = isRegisterMode ? "Ro'yxatdan O'tish" : "Tizimga Kirish";
            document.getElementById('phoneGroup').style.display = isRegisterMode ? "block" : "none";
            document.getElementById('toggleLink').innerText = isRegisterMode ? "Kirish rejimiga o'tish" : "Ro'yxatdan o'tish rejimiga o'tish";
        }

        function showMarket() {
            document.getElementById('authBox').style.display = 'none';
            document.getElementById('marketPage').style.display = 'block';
            loadElonlar();
        }

        function logout() {
            localStorage.removeItem('activeUser');
            location.reload();
        }

        async function handleAuth() {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const telefon = document.getElementById('telefon').value.trim();
            const msgBox = document.getElementById('msgBox');
            
            if(!username || !password) return;
            const url = isRegisterMode ? '/register' : '/login';
            const body = isRegisterMode ? { username, password, telefon } : { username, password };

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await res.json();
                if(res.ok) {
                    localStorage.setItem('activeUser', username);
                    showMarket();
                } else {
                    msgBox.innerText = data.detail || "Xato!";
                    msgBox.className = "message error";
                }
            } catch {
                msgBox.innerText = "Ulanish xatosi!";
                msgBox.className = "message error";
            }
        }

        async function loadElonlar() {
            try {
                const res = await fetch('/elonlar/');
                const elonlar = await res.json();
                const box = document.getElementById('elonlarRoʻyxati');
                box.innerHTML = '';
                if(elonlar.length === 0) {
                    box.innerHTML = '<p style="color:#999; text-align:center;">E\'lonlar yo\'q</p>';
                    return;
                }
                elonlar.forEach(e => {
                    box.innerHTML += `
                        <div class="elon-card">
                            <h5>\${e.sarlavha}</h5>
                            <p>\${e.tavsif || ''}</p>
                            <small>Tel: \${e.telefon || ''}</small>
                            <div style="color:green; font-weight:bold;">\${e.narx}</div>
                        </div>`;
                });
            } catch {}
        }

        async function addElon() {
            const sarlavha = document.getElementById('elonSarlavha').value;
            const tavsif = document.getElementById('elonTavsif').value;
            const narx = document.getElementById('elonNarx').value;
            const telefon = document.getElementById('elonTel').value;
            const elonMsg = document.getElementById('elonMsg');

            if(!sarlavha || !narx) return;

            try {
                const res = await fetch('/elonlar/yaratish/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sarlavha, tavsif, narx, telefon })
                });
                if(res.ok) {
                    elonMsg.innerText = "E'lon qo'shildi! ✨";
                    elonMsg.className = "message success";
                    document.getElementById('elonSarlavha').value = '';
                    document.getElementById('elonTavsif').value = '';
                    document.getElementById('elonNarx').value = '';
                    document.getElementById('elonTel').value = '';
                    loadElonlar();
                }
            } catch {}
        }
    </script>
    </body>
    </html>
    """

@app.post("/register")
def register_user(user: UserRegister):
    u = str(user.username).strip() if user.username else ""
    if not u: raise HTTPException(status_code=400, detail="Nomini yozing")
    if users_collection.find_one({"username": u}): raise HTTPException(status_code=400, detail="Band")
    users_collection.insert_one({"username": u, "password": str(user.password), "telefon": user.telefon})
    return {"message": "OK"}

@app.post("/login")
def login_user(user: UserLogin):
    u = str(user.username).strip() if user.username else ""
    db_user = users_collection.find_one({"username": u})
    if not db_user or str(db_user["password"]) != str(user.password):
        raise HTTPException(status_code=400, detail="Xato")
    return {"message": "OK"}

@app.get("/elonlar/")
def get_elonlar():
    try:
        elonlar = list(elonlar_collection.find({}).sort("_id", -1))
        for e in elonlar: 
            if "_id" in e: del e["_id"]
        return elonlar
    except:
        return []

@app.post("/elonlar/yaratish/")
def create_elon(elon: Elon):
    elonlar_collection.insert_one(elon.dict())
    return {"message": "OK"}
