from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Raqamli Bozor Platformasi")

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
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
            body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; flex-direction: column; }
            .container { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .main-page { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 600px; display: none; }
            .input-group { margin-bottom: 12px; }
            .input-group label { display: block; margin-bottom: 4px; color: #555; font-size: 14px; }
            .input-group input, .input-group textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; outline: none; }
            button { width: 100%; padding: 10px; background: #007bff; border: none; border-radius: 6px; color: white; font-size: 16px; cursor: pointer; font-weight: bold; }
            .message { margin-top: 10px; padding: 10px; border-radius: 6px; font-size: 14px; text-align: center; display: none; }
            .success { background: #d4edda; color: #155724; display: block; }
            .error { background: #f8d7da; color: #721c24; display: block; }
            .elon-card { background: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 8px; margin-bottom: 10px; text-align: left; }
        </style>
    </head>
    <body>

    <div class="container" id="authBox">
        <h2 id="formTitle" style="text-align:center; margin-bottom:15px;">Ro'yxatdan O'tish</h2>
        <div class="input-group">
            <label>Foydalanuvchi nomi</label>
            <input type="text" id="username" placeholder="Username">
        </div>
        <div class="input-group">
            <label>Parol</label>
            <input type="password" id="password" placeholder="Parol">
        </div>
        <div class="input-group" id="phoneGroup">
            <label>Telefon raqam</label>
            <input type="text" id="telefon" placeholder="+99899...">
        </div>
        <button onclick="handleAuth()">Yuborish</button>
        <div id="msgBox" class="message"></div>
        <p id="toggleLink" onclick="toggleForm()" style="text-align:center; margin-top:15px; color:#007bff; cursor:pointer; font-size:14px; text-decoration: underline;">Sizda profil bormi? Kirish</p>
    </div>

    <div class="main-page" id="marketPage">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px; align-items:center; border-bottom: 2px solid #eee; padding-bottom: 10px;">
            <h3>🚀 Raqamli Bozor</h3>
            <button onclick="logout()" style="width:auto; background:#dc3545; padding:5px 15px;">Chiqish 🚪</button>
        </div>
        
        <div style="background: #fdfdfd; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 20px;">
            <h4 style="margin-bottom: 10px;">Yangi e'lon joylashtirish</h4>
            <div class="input-group"><input type="text" id="elonSarlavha" placeholder="E'lon sarlavhasi"></div>
            <div class="input-group"><textarea id="elonTavsif" placeholder="Tavsif"></textarea></div>
            <div class="input-group"><input type="text" id="elonNarx" placeholder="Narxi"></div>
            <div class="input-group"><input type="text" id="elonTel" placeholder="Telefon raqam"></div>
            <button onclick="addElon()" style="background:#28a745;">E'lon joylash ✨</button>
            <div id="elonMsg" class="message"></div>
        </div>

        <h4>Barcha faol e'lonlar:</h4>
        <div id="elonlarRoʻyxati" style="margin-top:10px;"></div>
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
            document.getElementById('toggleLink').innerText = isRegisterMode ? "Sizda profil bormi? Kirish" : "Yangi profil yaratish (Ro'yxatdan o'tish)";
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

        function handleAuth() {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const msgBox = document.getElementById('msgBox');
            
            if(!username || !password) {
                msgBox.innerText = "Hamma maydonlarni to'ldiring!";
                msgBox.className = "message error";
                return;
            }

            if (isRegisterMode) {
                let users = JSON.parse(localStorage.getItem('users_db')) || [];
                if (users.some(u => u.username === username)) {
                    msgBox.innerText = "Bu foydalanuvchi nomi band!";
                    msgBox.className = "message error";
                    return;
                }
                users.push({ username, password });
                localStorage.setItem('users_db', JSON.stringify(users));
            } else {
                let users = JSON.parse(localStorage.getItem('users_db')) || [];
                let userExists = users.find(u => u.username === username && u.password === password);
                if (!userExists) {
                    msgBox.innerText = "Login yoki parol xato!";
                    msgBox.className = "message error";
                    return;
                }
            }

            localStorage.setItem('activeUser', username);
            showMarket();
        }

        function loadElonlar() {
            const box = document.getElementById('elonlarRoʻyxati');
            box.innerHTML = '';
            
            // Standart e'lonlar va foydalanuvchi e'lonlarini birlashtiramiz
            let localElonlar = JSON.parse(localStorage.getItem('elonlar_db')) || [];
            
            if(localElonlar.length === 0) {
                box.innerHTML = '<p style="color:#999; text-align:center; padding: 20px;">Hozircha faol e\'lonlar yo\'q.</p>';
                return;
            }

            localElonlar.reverse().forEach(e => {
                box.innerHTML += `
                    <div class="elon-card">
                        <h5 style="color:#333; font-size:16px; font-weight:600;">\${e.sarlavha}</h5>
                        <p style="color:#666; font-size:14px; margin:5px 0;">\${e.tavsif || ''}</p>
                        <small style="color:#888;">📞 Tel: \${e.telefon || ''}</small>
                        <div style="color:#28a745; font-weight:bold; font-size:16px; margin-top:5px;">\${e.narx}</div>
                    </div>`;
            });
        }

        function addElon() {
            const sarlavha = document.getElementById('elonSarlavha').value.trim();
            const tavsif = document.getElementById('elonTavsif').value.trim();
            const narx = document.getElementById('elonNarx').value.trim();
            const telefon = document.getElementById('elonTel').value.trim();
            const elonMsg = document.getElementById('elonMsg');

            if(!sarlavha || !narx) {
                elonMsg.innerText = "Sarlavha va narxni yozing!";
                elonMsg.className = "message error";
                return;
            }

            let localElonlar = JSON.parse(localStorage.getItem('elonlar_db')) || [];
            localElonlar.push({ sarlavha, tavsif, narx, telefon });
            localStorage.setItem('elonlar_db', JSON.stringify(localElonlar));

            elonMsg.innerText = "E'lon muvaffaqiyatli qo'shildi! ✨";
            elonMsg.className = "message success";
            
            document.getElementById('elonSarlavha').value = '';
            document.getElementById('elonTavsif').value = '';
            document.getElementById('elonNarx').value = '';
            document.getElementById('elonTel').value = '';
            
            loadElonlar();
        }
    </script>
    </body>
    </html>
    """
