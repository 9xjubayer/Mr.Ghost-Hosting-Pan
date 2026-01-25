from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, jsonify, flash
import os, zipfile, subprocess, shutil, json

app = Flask(__name__)
app.secret_key = "jubayer_hosting_v5_final"

UPLOAD_FOLDER = "uploads"
DB_FILE = "database.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

processes = {}

# --- ডাটাবেস ফাংশন ---
def load_db():
    if not os.path.exists(DB_FILE):
        default = {"user_pw": "ghost34", "users": {}}
        with open(DB_FILE, "w") as f: json.dump(default, f)
        return default
    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
            if "users" not in data: data["users"] = {}
            if "user_pw" not in data: data["user_pw"] = "12345"
            return data
        except:
            return {"user_pw": "12345", "users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

ADMIN_PASS = "2332"

# --- Login HTML (Get Password সেকশন যুক্ত করা হয়েছে) ---
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | Ultra Hosting</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #050505; --primary: #00ffff; --sec: #ff00ff; }
        body { background: #050505; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
        #particles-js { position: fixed; width: 100%; height: 100%; z-index: 1; }
        .login-card { position: relative; z-index: 10; background: rgba(15,20,30,0.9); padding: 30px; border-radius: 20px; width: 320px; text-align: center; border: 1px solid rgba(0,255,255,0.1); backdrop-filter: blur(10px); }
        input, select { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid #333; background: rgba(0,0,0,0.5); color: white; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 14px; border-radius: 10px; border: none; background: linear-gradient(135deg, var(--primary), var(--sec)); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; transition: 0.3s; }
        button:hover { opacity: 0.8; transform: scale(1.02); }
        .flash { background: rgba(255,0,0,0.2); color: #ff4d4d; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-size: 13px; border: 1px solid #ff4d4d; }
        .get-pass { margin-top: 20px; font-size: 13px; color: #aaa; border-top: 1px solid #222; padding-top: 15px; }
        .get-pass a { color: var(--primary); text-decoration: none; font-weight: bold; }
        .get-pass i { margin-right: 5px; }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    <div class="login-card">
        <i class="fa-solid fa-bolt" style="font-size: 40px; color: var(--primary);"></i>
        <h2>SYSTEM LOGIN</h2>
        {% with messages = get_flashed_messages() %}{% if messages %}{% for msg in messages %}<div class="flash">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}
        <form method="post" action="/login">
            <select name="login_type"><option value="user">USER ACCESS</option><option value="admin">ADMIN ROOT</option></select>
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">LOGIN NOW</button>
        </form>
        
        <div class="get-pass">
            <span>Don't have a password?</span><br>
            <a href="https://t.me/mrghostfileshare34/3" target="_blank">
                <i class="fa-brands fa-telegram"></i> GET PASSWORD
            </a>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>particlesJS('particles-js', {"particles":{"number":{"value":80},"color":{"value":"#00ffff"},"line_linked":{"enable":true,"color":"#ff00ff"},"move":{"enable":true,"speed":2}}});</script>
</body>
</html>
'''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        l_type = request.form.get("login_type")
        username = request.form.get("username", "").strip()
        pw = request.form.get("password", "").strip()
        db = load_db()
        session.clear()

        if l_type == "admin":
            if username == "admin" and pw == ADMIN_PASS:
                session['is_admin'], session['username'] = True, "admin"
                return redirect(url_for("admin_panel"))
            else: flash("Invalid Admin Password!")
        else:
            correct_pw = db["users"].get(username, db["user_pw"])
            if username and pw == correct_pw:
                session['is_admin'], session['username'] = False, username
                return redirect(url_for("index"))
            else: flash("Invalid Username or Password!")
    
    return render_template_string(LOGIN_HTML)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get('is_admin'): return redirect(url_for("login"))
    db = load_db()
    msg = ""
    
    if request.method == "POST":
        if "new_pw" in request.form:
            db["user_pw"] = request.form.get("new_pw")
            save_db(db)
            msg = "Global Pass Updated!"
        elif "target_user" in request.form:
            target = request.form.get("target_user")
            new_u_pass = request.form.get("new_user_pass")
            db["users"][target] = new_u_pass
            save_db(db)
            msg = f"Key for @{target} updated!"

    user_stats = []
    if os.path.exists(UPLOAD_FOLDER):
        for u_name in os.listdir(UPLOAD_FOLDER):
            u_path = os.path.join(UPLOAD_FOLDER, u_name)
            if os.path.isdir(u_path) and u_name != "admin":
                total_projects = len([d for d in os.listdir(u_path) if os.path.isdir(os.path.join(u_path, d))])
                active_bots = sum(1 for (user, bot), p in processes.items() if user == u_name and p.poll() is None)
                u_pass = db["users"].get(u_name, db["user_pw"])
                user_stats.append({"name": u_name, "projects": total_projects, "active": active_bots, "pass": u_pass})

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Control</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root { --bg: #030508; --accent: #00d2ff; --border: rgba(255,255,255,0.1); }
            body { background: var(--bg); color: #fff; font-family: sans-serif; margin: 0; padding: 15px; }
            .container { max-width: 500px; margin: auto; position: relative; z-index: 5; }
            .card { background: rgba(255,255,255,0.05); border: 1px solid var(--border); border-radius: 15px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(10px); }
            input { background: #000; border: 1px solid #333; color: #fff; padding: 10px; border-radius: 8px; width: 70%; }
            button { background: var(--accent); border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: bold; }
            .user-box { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; padding: 10px 0; }
            .online { color: #39ff14; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h3><i class="fa-solid fa-user-shield"></i> ROOT ADMIN</h3>
            {% if msg %}<p style="color:cyan; text-align:center;">{{msg}}</p>{% endif %}
            
            <div class="card">
                <p>Global Key: <b>{{db['user_pw']}}</b></p>
                <form method="post"><input type="text" name="new_pw" placeholder="New Global Pass"><button type="submit">SET</button></form>
            </div>

            {% for u in user_stats %}
            <div class="card">
                <div class="user-box">
                    <span><b>@{{u.name}}</b> ({{u.projects}} Apps)</span>
                    <span class="online">● {{u.active}} Active</span>
                </div>
                <p style="font-size:12px; color:#aaa;">Key: {{u.pass}}</p>
                <form method="post">
                    <input type="hidden" name="target_user" value="{{u.name}}">
                    <input type="text" name="new_user_pass" placeholder="Change Key">
                    <button type="submit"><i class="fa-solid fa-sync"></i></button>
                </form>
            </div>
            {% endfor %}
            <a href="/" style="color:#aaa; text-decoration:none; display:block; text-align:center; margin-top:20px;">Back to Home</a>
        </div>
    </body>
    </html>
    ''', db=db, user_stats=user_stats, msg=msg)

@app.route("/")
def index():
    if 'username' not in session or session.get('is_admin'): return redirect(url_for("login"))
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
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(extract_dir)
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

@app.route("/delete/<name>")
def delete(name):
    user_name = session.get('username')
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    stop(name)
    if os.path.exists(app_dir): shutil.rmtree(app_dir)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3642, debug=True)
