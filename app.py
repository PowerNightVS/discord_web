from flask import Flask, render_template, redirect, request, session, url_for
import os
import requests
from dotenv import load_dotenv

# ---------------- Load environment variables ---------------- #
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ---------------- Discord OAuth2 & Bot Setup ---------------- #
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
SUPPORT_LINK = os.getenv("SUPPORT_LINK")
INVITE_LINK = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot+applications.commands&permissions=8"
DISCORD_API = "https://discord.com/api"

# ---------------- Utility Functions ---------------- #
def get_current_user():
    return session.get("user")

def check_bot_status():
    return True  # Placeholder: replace with real logic

def get_bot_wake_up_time():
    return "08:00 AM"

def get_bot_guilds():
    """Fetch servers the bot is in"""
    url = f"{DISCORD_API}/users/@me/guilds"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    guilds = response.json()
    for g in guilds:
        g['icon_url'] = (
            f"https://cdn.discordapp.com/icons/{g['id']}/{g['icon']}.png"
            if g.get('icon') else url_for('static', filename='default_icon.png')
        )
        g['members'] = g.get('approximate_member_count', 'Unknown')
        g['description'] = g.get('description', 'No description')
    return guilds

# ---------------- Routes ---------------- #
@app.route("/")
def index():
    joined_servers = get_bot_guilds()
    return render_template(
        "index.html",
        joined_servers=joined_servers,
        invite_link=INVITE_LINK,
        support_link=SUPPORT_LINK
    )

# --- Add this near your other lists (like commands) ---
active_streams = [] 

# --- Add these two new routes ---

@app.route("/api/add_stream", methods=["POST"])
def add_stream():
    """Endpoint for the Discord Bot to send stream data"""
    data = request.json
    # Basic data: {'streamer': 'Name', 'title': 'Title', 'quality': '1080p'}
    if data:
        # Keep only the last 10 streams so the list doesn't get too long
        active_streams.insert(0, data)
        if len(active_streams) > 10:
            active_streams.pop()
        return {"status": "success"}, 200
    return {"status": "error"}, 400

@app.route("/stream")
def stream_page():
    """The steam.html page list"""
    return render_template("stream.html", streams=active_streams)

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/login")
def login():
    return redirect(
        f"{DISCORD_API}/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        "&response_type=code&scope=identify%20email%20guilds"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify email guilds",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
    if r.status_code != 200:
        return "Failed to authorize with Discord", 400

    tokens = r.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return "No access token received", 400

    user_resp = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if user_resp.status_code != 200:
        return "Failed to fetch user info", 400

    session["user"] = user_resp.json()
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = get_current_user()
    commands = [
        {"name": "/play", "description": "Play a song"},
        {"name": "/nowplaying", "description": "See current song"},
        {"name": "/queue", "description": "Show the song queue"},
        {"name": "/radio", "description": "Play a radio station"},
        {"name": "/resume", "description": "Resume playback"},
        {"name": "/loop", "description": "Loop current song or queue"},
        {"name": "/leave", "description": "Make the bot leave VC"},
        {"name": "/join", "description": "Make the bot join VC"},
        {"name": "/invite", "description": "Get bot invite link"},
        {"name": "/bass", "description": "Adjust bass"},
        {"name": "/lyrics", "description": "Show song lyrics"},
        {"name": "/shuffle", "description": "Shuffle the queue"},
        {"name": "/skip", "description": "Skip the current song"},
        {"name": "/volume", "description": "Adjust volume"}
    ]

    return render_template(
        "dashboard.html",
        user=user,
        commands=commands,
        bot_online=check_bot_status(),
        bot_wake_up_time=get_bot_wake_up_time(),
        invite_link=INVITE_LINK
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
