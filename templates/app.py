from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, jsonify
import os, zipfile, subprocess, shutil, json, time

app = Flask(__name__)
app.secret_key = "jubayer_hosting_v5_final_pro"

UPLOAD_FOLDER = "uploads"
DB_FILE = "database.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

processes = {}

def load_db():
    if not os.path.exists(DB_FILE):
        default = {"user_pw": "ghost34", "users": {}, "start_times": {}}
        with open(DB_FILE, "w") as f: json.dump(default, f)
        return default
    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
            if "users" not in data: data["users"] = {}
            if "user_pw" not in data: data["user_pw"] = "ghost34"
            if "start_times" not in data: data["start_times"] = {}
            return data
        except:
            return {"user_pw": "ghost34", "users": {}, "start_times": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

ADMIN_PASS = "2332"

# --- LOGIN PAGE (Premium Glassmorphism Style) ---
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | Ultra Hosting</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { 
            --bg: #030508; 
            --primary: #00ffff; 
            --sec: #7000ff; 
            --glass: rgba(255, 255, 255, 0.03);
        }

        body { 
            background: var(--bg); 
            color: white; 
            font-family: 'Orbitron', sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
            overflow: hidden; 
        }

        #particles-js { position: fixed; width: 100%; height: 100%; z-index: 1; }

        /* Outer Glow Card */
        .login-card { 
            position: relative; 
            z-index: 10; 
            background: var(--glass); 
            padding: 40px 30px; 
            border-radius: 25px; 
            width: 340px; 
            text-align: center; 
            border: 1px solid rgba(0, 255, 255, 0.15); 
            backdrop-filter: blur(20px);
            box-shadow: 0 25px 45px rgba(0,0,0,0.5), inset 0 0 15px rgba(0, 255, 255, 0.05);
            transition: 0.4s;
        }

        .login-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.15);
        }

        /* Animated Lock Icon */
        .lock-container {
            width: 80px;
            height: 80px;
            background: rgba(0, 255, 255, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            border: 2px solid var(--primary);
            box-shadow: 0 0 20px var(--primary);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 10px var(--primary); }
            50% { transform: scale(1.05); box-shadow: 0 0 25px var(--primary); }
            100% { transform: scale(1); box-shadow: 0 0 10px var(--primary); }
        }

        .lock-icon { font-size: 35px; color: var(--primary); }

        h2 { 
            font-size: 20px; 
            margin-bottom: 25px; 
            letter-spacing: 4px; 
            text-transform: uppercase;
            background: linear-gradient(to right, #fff, var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        input, select { 
            width: 100%; 
            padding: 14px; 
            margin: 10px 0; 
            border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.1); 
            background: rgba(255,255,255,0.05); 
            color: #fff; 
            outline: none; 
            font-size: 14px;
            transition: 0.3s;
        }

        input:focus { 
            background: rgba(255,255,255,0.1); 
            border-color: var(--primary); 
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        }

        button { 
            width: 100%; 
            padding: 15px; 
            border-radius: 12px; 
            border: none; 
            background: linear-gradient(45deg, var(--sec), var(--primary)); 
            color: #fff; 
            font-weight: bold; 
            font-size: 15px;
            cursor: pointer; 
            margin-top: 15px; 
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: 0.4s;
        }

        button:hover { 
            letter-spacing: 4px; 
            box-shadow: 0 0 20px var(--primary);
            opacity: 0.9;
        }

        .get-pw { margin-top: 25px; font-size: 12px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }
        .get-pw a { 
            color: var(--primary); 
            text-decoration: none; 
            font-weight: bold; 
            display: inline-flex; 
            align-items: center; 
            gap: 8px; 
            transition: 0.3s;
        }
        .get-pw a:hover { transform: translateY(-2px); text-shadow: 0 0 10px var(--primary); }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    <div class="login-card">
        <div class="lock-container">
            <i class="fa-solid fa-user-shield lock-icon"></i>
        </div>
        
        <h2>System Login</h2>
        
        <form method="post" action="/login">
            <select name="login_type">
                <option value="user">USER ACCESS</option>
                <option value="admin">ADMIN ROOT</option>
            </select>
            <input type="text" name="username" placeholder="Enter Nickname" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Access System</button>
        </form>
        
        <div class="get-pw">
            <a href="https://t.me/mr_ghost34" target="_blank">
                <i class="fa-brands fa-telegram"></i> FORGOT PASSWORD?
            </a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 100, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#00ffff" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.5, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#00ffff", "opacity": 0.2, "width": 1 },
                "move": { "enable": true, "speed": 2, "direction": "none", "random": false, "straight": false, "out_mode": "out", "bounce": false }
            }
        });
    </script>
</body>
</html>
'''



# --- ADMIN PANEL HTML (Modern Dashboard Version) ---
ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Root | Ultra Hosting</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #0a0b10; --card: #161b22; --accent: #00ffff; --text: #e6edf3; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .header h2 { font-size: 24px; color: var(--accent); letter-spacing: 1px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
        .stat-card i { font-size: 25px; color: var(--accent); margin-bottom: 10px; }
        .stat-card div { font-size: 20px; font-weight: bold; }

        .card { background: var(--card); padding: 20px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; }
        h3 { margin-top: 0; font-size: 18px; color: var(--accent); display: flex; align-items: center; gap: 10px; }

        .input-group { display: flex; gap: 10px; margin-top: 15px; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
        input:focus { border-color: var(--accent); }

        .btn { padding: 10px 20px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; display: inline-flex; align-items: center; gap: 5px; text-decoration: none; }
        .btn-primary { background: var(--accent); color: #000; }
        .btn-primary:hover { opacity: 0.8; box-shadow: 0 0 10px var(--accent); }
        .btn-logout { background: #ff4757; color: white; font-size: 13px; }

        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; min-width: 600px; }
        th { text-align: left; padding: 15px; border-bottom: 2px solid #30363d; color: #8b949e; }
        td { padding: 15px; border-bottom: 1px solid #21262d; }
        
        .user-link { color: var(--accent); text-decoration: none; font-weight: bold; }
        .project-tag { background: rgba(0,255,255,0.1); color: var(--accent); padding: 3px 8px; border-radius: 5px; font-size: 12px; display: inline-block; margin-bottom: 3px; border: 1px solid rgba(0,255,255,0.2); }
        
        .action-btns { display: flex; gap: 8px; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h2><i class="fa-solid fa-shield-halved"></i> ADMIN ROOT</h2>
        <a href="/logout" class="btn btn-logout"><i class="fa-solid fa-power-off"></i> LOGOUT</a>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fa-solid fa-users"></i>
            <p>Total Users</p>
            <div>{{ users|length }}</div>
        </div>
        <div class="stat-card">
            <i class="fa-solid fa-rocket"></i>
            <p>Active Projects</p>
            <div>{{ start_times|length }}</div>
        </div>
    </div>
    
    <div class="card">
        <h3><i class="fa-solid fa-gears"></i> Global System Settings</h3>
        <form action="/admin/global_pw" method="post" class="input-group">
            <input type="text" name="global_pw" value="{{ global_pw }}" placeholder="Set Default Password">
            <button type="submit" class="btn btn-primary">Update Password</button>
        </form>
    </div>

    <div class="card">
        <h3><i class="fa-solid fa-user-gear"></i> User Management</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>User Password</th>
                        <th>Active Deployments</th>
                        <th>Control</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u_name, u_pw in users.items() %}
                    <tr>
                        <td>
                            <a href="/admin/view_user/{{ u_name }}" class="user-link">
                                <i class="fa-solid fa-circle-user"></i> {{ u_name }}
                            </a>
                        </td>
                        <td>
                            <form action="/admin/change_pw" method="post" style="display:flex; gap:5px;">
                                <input type="hidden" name="username" value="{{ u_name }}">
                                <input type="text" name="new_pw" value="{{ u_pw }}" style="width:100px; padding:5px;">
                                <button type="submit" class="btn btn-primary btn-sm">Save</button>
                            </form>
                        </td>
                        <td>
                            {% set count = namespace(value=0) %}
                            {% for p_key in start_times.keys() %}
                                {% if p_key.startswith(u_name + '_') %}
                                    <span class="project-tag">● {{ p_key.split('_')[1] }}</span><br>
                                    {% set count.value = count.value + 1 %}
                                {% endif %}
                            {% endfor %}
                            {% if count.value == 0 %}
                                <span style="color:#444;">No active bots</span>
                            {% endif %}
                        </td>
                        <td class="action-btns">
                            <a href="/admin/login_as/{{ u_name }}" class="btn btn-primary btn-sm" style="background:#fff;">
                                <i class="fa-solid fa-right-to-bracket"></i> Login As
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''


# --- BACKEND LOGIC ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        l_type = request.form.get("login_type")
        username = request.form.get("username", "").strip() # Nickname
        pw = request.form.get("password", "").strip()
        db = load_db()
        if l_type == "admin":
            if username == "admin" and pw == ADMIN_PASS:
                session['is_admin'], session['username'] = True, "admin"
                return redirect(url_for("admin_panel"))
        else:
            if username and username not in db["users"]:
                db["users"][username] = db["user_pw"]
                save_db(db)
            if username and pw == db["users"].get(username):
                session['is_admin'], session['username'] = False, username
                return redirect(url_for("index"))
    return render_template_string(LOGIN_HTML)

@app.route("/")
def index():
    if 'username' not in session: return redirect(url_for("login"))
    user_name = session['username'] # This is the Nickname
    user_dir = os.path.join(UPLOAD_FOLDER, user_name)
    os.makedirs(user_dir, exist_ok=True)
    apps_list = []
    for name in os.listdir(user_dir):
        if os.path.isdir(os.path.join(user_dir, name)):
            p = processes.get((user_name, name))
            apps_list.append({"name": name, "running": (p and p.poll() is None)})
    return render_template("index.html", apps=apps_list, username=user_name)

# --- ADMIN ROUTES ---
@app.route("/admin")
def admin_panel():
    if not session.get('is_admin'): return redirect(url_for("login"))
    db = load_db()
    return render_template_string(ADMIN_HTML, users=db["users"], start_times=db["start_times"], global_pw=db["user_pw"])

@app.route("/admin/global_pw", methods=["POST"])
def global_pw():
    db = load_db()
    db["user_pw"] = request.form.get("global_pw")
    save_db(db)
    return redirect(url_for("admin_panel"))

@app.route("/admin/change_pw", methods=["POST"])
def change_pw():
    u_name, new_pw = request.form.get("username"), request.form.get("new_pw")
    db = load_db()
    if u_name in db["users"]:
        db["users"][u_name] = new_pw
        save_db(db)
    return redirect(url_for("admin_panel"))

@app.route("/admin/login_as/<username>")
def login_as(username):
    session['username'], session['is_admin'] = username, False
    return redirect(url_for("index"))

@app.route("/admin/view_user/<username>")
def view_user(username):
    session['username'] = username
    return redirect(url_for("index"))

# --- CORE OPS ---
@app.route("/run/<name>")
def run(name):
    user_name = session['username']
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    extract_dir = os.path.join(app_dir, "extracted")
    if (user_name, name) not in processes or processes[(user_name, name)].poll() is not None:
        main_file = next((f for f in ["main.py", "bot.py", "app.py", "index.js", "server.js"] if os.path.exists(os.path.join(extract_dir, f))), None)
        if main_file:
            log_path = os.path.join(app_dir, "logs.txt")
            log_file = open(log_path, "w")
            cmd = ["python", main_file] if main_file.endswith('.py') else ["node", main_file]
            processes[(user_name, name)] = subprocess.Popen(cmd, cwd=extract_dir, stdout=log_file, stderr=log_file, text=True)
            db = load_db()
            db["start_times"][f"{user_name}_{name}"] = int(time.time() * 1000)
            save_db(db)
    return redirect(url_for("index"))

@app.route("/get_log/<name>")
def get_log(name):
    user_name = session.get('username')
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    log_path = os.path.join(app_dir, "logs.txt")
    log_content = ""
    if os.path.exists(log_path):
        with open(log_path, "r") as f: log_content = f.read()[-2000:]
    p = processes.get((user_name, name))
    db = load_db()
    is_running = (p and p.poll() is None)
    return jsonify({
        "log": log_content, 
        "status": "RUNNING" if is_running else "OFFLINE", 
        "start_time": db["start_times"].get(f"{user_name}_{name}", 0)
    })

@app.route("/stop/<name>")
def stop(name):
    user_name = session.get('username')
    p = processes.get((user_name, name))
    if p: p.terminate(); del processes[(user_name, name)]
    db = load_db()
    if f"{user_name}_{name}" in db["start_times"]:
        del db["start_times"][f"{user_name}_{name}"]
        save_db(db)
    return redirect(url_for("index"))

@app.route("/upload", methods=["POST"])
def upload():
    user_name = session['username']
    file = request.files.get("file")
    if file and file.filename.endswith(".zip"):
        app_name = file.filename.rsplit('.', 1)[0]
        user_dir = os.path.join(UPLOAD_FOLDER, user_name, app_name)
        os.makedirs(user_dir, exist_ok=True)
        zip_path = os.path.join(user_dir, file.filename)
        file.save(zip_path)
        extract_dir = os.path.join(user_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        os.remove(zip_path)
    return redirect(url_for("index"))

@app.route("/restart/<name>")
def restart(name):
    stop(name)
    time.sleep(1)
    return run(name)

@app.route("/delete/<name>")
def delete(name):
    user_name = session.get('username')
    stop(name)
    app_dir = os.path.join(UPLOAD_FOLDER, user_name, name)
    if os.path.exists(app_dir): shutil.rmtree(app_dir)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3522, debug=True)
