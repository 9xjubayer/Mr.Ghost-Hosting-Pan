from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, zipfile, subprocess, shutil, json, time

app = Flask(__name__)
app.secret_key = "jubayer_ultra_hosting_final_v3"

UPLOAD_FOLDER = "uploads"
DB_FILE = "database.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

processes = {}

# --- ডাটাবেস ফাংশন ---
def load_db():
    if not os.path.exists(DB_FILE):
        default = {"user_pw": "12345"}
        with open(DB_FILE, "w") as f: json.dump(default, f)
        return default
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

ADMIN_PASS = "jubayer999"

# --- Routes ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        l_type = request.form.get("login_type")
        username = request.form.get("username", "").strip()
        pw = request.form.get("password", "").strip()
        db = load_db()

        if l_type == "admin":
            if username == "admin" and pw == ADMIN_PASS:
                session['is_admin'], session['username'] = True, "admin"
                return redirect(url_for("admin_panel"))
        else:
            if username and pw == db["user_pw"]:
                session['is_admin'], session['username'] = False, username
                return redirect(url_for("index"))
    
    return render_template("login.html") if os.path.exists("templates/login.html") else redirect("/static_login")

@app.route("/static_login")
def static_login():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Terminal Access | Ultra Hosting</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --bg: #020408;
                --card: rgba(15, 20, 30, 0.9);
                --border: #30363d;
                --primary: #00d2ff;
                --secondary: #3a86ff;
                --text: #ffffff;
            }
            * { box-sizing: border-box; }
            body {
                background: var(--bg);
                color: var(--text);
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                overflow: hidden;
            }

            /* --- Mega Background Animation --- */
            .bg-layer {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                z-index: -1;
                background: radial-gradient(circle at 50% 50%, #0a1128 0%, #020408 100%);
            }
            .orbit {
                position: absolute;
                border: 1px solid rgba(0, 210, 255, 0.05);
                border-radius: 50%;
                animation: spin linear infinite;
            }
            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

            /* --- The MEGA Login Card --- */
            .login-card {
                background: var(--card);
                backdrop-filter: blur(30px);
                padding: 80px 60px; /* অনেক বড় প্যাডিং */
                border-radius: 40px;
                width: 95%;
                max-width: 650px; /* বক্সের সাইজ আরও বাড়ানো হয়েছে */
                border: 1.5px solid rgba(255,255,255,0.08);
                box-shadow: 0 40px 100px rgba(0,0,0,0.8), inset 0 0 20px rgba(0, 210, 255, 0.05);
                text-align: center;
                animation: zoomIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            @keyframes zoomIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
            
            .logo-header { margin-bottom: 50px; }
            .logo-icon {
                font-size: 80px; /* বড় আইকন */
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                filter: drop-shadow(0 0 10px rgba(0, 210, 255, 0.5));
            }
            h2 { font-size: 3rem; margin: 15px 0; font-weight: 900; letter-spacing: -1px; }
            p { color: #8b949e; font-size: 18px; margin-bottom: 50px; }
            
            .input-group { text-align: left; margin-bottom: 30px; }
            label { display: block; font-size: 14px; margin-bottom: 12px; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
            
            select, input {
                width: 100%;
                padding: 22px 25px; /* ইনপুট বড় করা হয়েছে */
                border-radius: 20px;
                border: 2px solid var(--border);
                background: rgba(0, 0, 0, 0.4);
                color: white;
                font-size: 20px;
                transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                outline: none;
            }
            select:focus, input:focus {
                border-color: var(--primary);
                background: rgba(0, 0, 0, 0.6);
                box-shadow: 0 0 25px rgba(0, 210, 255, 0.3);
                transform: translateY(-2px);
            }
            
            button {
                width: 100%;
                padding: 24px;
                margin-top: 20px;
                border-radius: 20px;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: #000;
                font-weight: 900;
                border: none;
                cursor: pointer;
                font-size: 22px;
                text-transform: uppercase;
                letter-spacing: 2px;
                transition: 0.4s;
                box-shadow: 0 15px 35px rgba(0, 210, 255, 0.4);
            }
            button:hover { 
                transform: translateY(-5px);
                box-shadow: 0 20px 45px rgba(0, 210, 255, 0.6);
                filter: brightness(1.1);
            }
            
            .footer-text { margin-top: 50px; font-size: 14px; color: #444; font-weight: 600; }
            .status-dot { height: 10px; width: 10px; background: #39ff14; border-radius: 50%; display: inline-block; margin-right: 5px; box-shadow: 0 0 10px #39ff14; }
        </style>
    </head>
    <body>
        <div class="bg-layer">
            <div class="orbit" style="width: 800px; height: 800px; top: -10%; right: -10%; animation-duration: 60s;"></div>
            <div class="orbit" style="width: 600px; height: 600px; bottom: -5%; left: -5%; animation-duration: 40s; animation-direction: reverse;"></div>
        </div>

        <div class="login-card">
            <div class="logo-header">
                <div class="logo-icon"><i class="fa-solid fa-shield-halved"></i></div>
                <h2>HOSTING PANEL V1</h2>
                <p>সাদিয়া কেন আমার হলো না 😭</p>
            </div>
            
            <form method="post" action="/login">
                <div class="input-group">
                    <label><i class="fa-solid fa-layer-group"></i> ACCESS LEVEL</label>
                    <select name="login_type">
                        <option value="user">STANDARD USER</option>
                        <option value="admin">ROOT ADMINISTRATOR</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label><i class="fa-solid fa-user"></i> IDENTIFICATION</label>
                    <input type="text" name="username" placeholder="Yor Name" required>
                </div>
                
                <div class="input-group">
                    <label><i class="fa-solid fa-key"></i> ENCRYPTION KEY</label>
                    <input type="password" name="password" placeholder="••••••••••••" required>
                </div>
                
                <button type="submit">AUTHORIZE ACCESS</button>
            </form>
            
            <div class="footer-text">
                <span class="status-dot"></span> SECURE SERVER ENCRYPTED &bull; 2026
            </div>
        </div>
    </body>
    </html>
    '''

# --- Admin ও অন্যান্য রুট আগের মতোই আছে ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get('is_admin'): return redirect(url_for("login"))
    db = load_db()
    msg = ""
    if request.method == "POST":
        new_pw = request.form.get("new_pw")
        if new_pw:
            db["user_pw"] = new_pw
            save_db(db)
            msg = "User Password Updated Successfully!"
    user_stats = []
    if os.path.exists(UPLOAD_FOLDER):
        for u_name in os.listdir(UPLOAD_FOLDER):
            u_path = os.path.join(UPLOAD_FOLDER, u_name)
            if os.path.isdir(u_path):
                total_projects = len([d for d in os.listdir(u_path) if os.path.isdir(os.path.join(u_path, d))])
                active_bots = sum(1 for (user, bot), p in processes.items() if user == u_name and p.poll() is None)
                user_stats.append({"name": u_name, "projects": total_projects, "active": active_bots})
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Admin Panel</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{ --bg: #0d1117; --card: #161b22; --border: #30363d; --primary: #00d2ff; --accent: #39ff14; }}
            body {{ background: var(--bg); color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; margin: 0; padding: 10px; }}
            .container {{ max-width: 500px; margin: 0 auto; padding-bottom: 50px; }}
            .card {{ background: var(--card); padding: 20px; border-radius: 16px; border: 1px solid var(--border); margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 5px; }}
            h2, h3 {{ margin: 0; color: var(--primary); font-size: 1.2rem; }}
            .user-card {{ background: #0d1117; padding: 15px; border-radius: 12px; border: 1px solid var(--border); margin-top: 10px; }}
            .badge {{ background: var(--accent); color: black; font-size: 11px; padding: 3px 8px; border-radius: 20px; font-weight: bold; }}
            input {{ width: 100%; padding: 12px; margin: 12px 0; border-radius: 8px; background: var(--bg); color: white; border: 1px solid var(--border); box-sizing: border-box; outline: none; }}
            .btn {{ background: var(--primary); color: black; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: 800; cursor: pointer; text-transform: uppercase; }}
            .nav-link {{ color: #8b949e; text-decoration: none; font-size: 14px; border: 1px solid var(--border); padding: 5px 12px; border-radius: 6px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2><i class="fa-solid fa-user-shield"></i> Admin Panel</h2>
                <a href="/" class="nav-link">Dashboard</a>
            </div>
            <div class="card">
                <h3 style="color: #ffd700;"><i class="fa-solid fa-gears"></i> System Control</h3>
                <p style="font-size: 13px; color: #8b949e;">User Password: <b style="color: white;">{db['user_pw']}</b></p>
                {f'<p style="color: var(--accent); font-size: 12px;">{msg}</p>' if msg else ''}
                <form method="post">
                    <input type="text" name="new_pw" placeholder="Set New Global Password" required>
                    <button type="submit" class="btn">Update Password</button>
                </form>
            </div>
            <h3><i class="fa-solid fa-users"></i> Users ({len(user_stats)})</h3>
            {"".join([f"""
            <div class="user-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #58a6ff; font-weight: bold;">@{u['name']}</span>
                    <span class="badge">{u['active']} Active</span>
                </div>
                <p style="font-size: 13px; color: #8b949e; margin: 8px 0 0 0;">📂 Projects Hosted: <b>{u['projects']}</b></p>
            </div>
            """ for u in user_stats]) if user_stats else "<p style='text-align:center; color:#555;'>No users yet.</p>"}
        </div>
    </body>
    </html>
    '''

@app.route("/")
def index():
    if 'username' not in session: return redirect(url_for("login"))
    user_name = session['username']
    user_dir = os.path.join(UPLOAD_FOLDER, user_name)
    os.makedirs(user_dir, exist_ok=True)
    apps_list = []
    for name in os.listdir(user_dir):
        if os.path.isdir(os.path.join(user_dir, name)):
            p = processes.get((user_name, name))
            apps_list.append({"name": name, "running": (p and p.poll() is None)})
    return render_template("index.html", apps=apps_list, username=user_name)

@app.route("/upload", methods=["POST"])
def upload():
    if 'username' not in session: return redirect(url_for("login"))
    file = request.files.get('file')
    if file and file.filename.endswith('.zip'):
        user_name = session['username']
        user_dir = os.path.join(UPLOAD_FOLDER, user_name)
        app_name = file.filename.rsplit('.', 1)[0]
        app_dir = os.path.join(user_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)
        zip_path = os.path.join(app_dir, "app.zip")
        file.save(zip_path)
        extract_dir = os.path.join(app_dir, "extracted")
        if os.path.exists(extract_dir): shutil.rmtree(extract_dir)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    return redirect(url_for("index"))

@app.route("/run/<name>")
def run(name):
    if 'username' not in session: return redirect(url_for("login"))
    user_name = session['username']
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    extract_dir = os.path.join(app_dir, "extracted")
    if (user_name, name) not in processes or processes[(user_name, name)].poll() is not None:
        main_file = next((f for f in ["main.py", "bot.py", "app.py"] if os.path.exists(os.path.join(extract_dir, f))), None)
        if main_file:
            log_path = os.path.join(app_dir, "logs.txt")
            log = open(log_path, "a")
            p = subprocess.Popen(["python", main_file], cwd=extract_dir, stdout=log, stderr=log)
            processes[(user_name, name)] = p
    return redirect(url_for("index"))

@app.route("/stop/<name>")
def stop(name):
    user_name = session.get('username')
    p = processes.get((user_name, name))
    if p: p.terminate(); del processes[(user_name, name)]
    return redirect(url_for("index"))

@app.route("/restart/<name>")
def restart(name):
    stop(name)
    time.sleep(1)
    return run(name)

@app.route("/delete/<name>")
def delete(name):
    user_name = session.get('username')
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    stop(name)
    if os.path.exists(app_dir): shutil.rmtree(app_dir)
    return redirect(url_for("index"))

@app.route("/get_log/<name>")
def get_log(name):
    user_name = session.get('username')
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    log_path = os.path.join(app_dir, "logs.txt")
    log_content = "No logs yet..."
    if os.path.exists(log_path):
        with open(log_path, "r") as f: log_content = f.read()[-1000:]
    p = processes.get((user_name, name))
    status = "RUNNING" if (p and p.poll() is None) else "OFFLINE"
    return jsonify({"log": log_content, "status": status})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3642, debug=True)
