from flask import Flask, render_template, redirect, request, session, url_for
import os
import requests
from dotenv import load_dotenv

# ---------------- Load environment variables ---------------- #
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
app.config['TEMPLATES_AUTO_RELOAD'] = True
# ---------------- Discord OAuth2 Setup ---------------- #
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
BOT_INVITE_LINK = (
    f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}"
    "&scope=bot+applications.commands&permissions=8"
)
DISCORD_API = "https://discord.com/api"

# ---------------- Utility Functions ---------------- #
def get_current_user():
    return session.get("user")

def check_bot_status():
    """Check if NightWave bot is online"""
    # TODO: Replace with real bot status check
    return True  # True = online, False = offline

def get_bot_wake_up_time():
    """Return bot wake-up time"""
    # TODO: Replace with real wake-up logic
    return "08:00 AM"

# ---------------- Routes ---------------- #
@app.route("/")
def index():
    """Landing page"""
    return render_template("index.html", invite_link=BOT_INVITE_LINK)

@app.route("/login")
def login():
    """Redirect user to Discord OAuth2 login"""
    return redirect(
        f"{DISCORD_API}/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=identify%20email%20guilds"
    )

@app.route("/callback")
def callback():
    """Handle Discord OAuth2 callback"""
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

    # Exchange code for access token
    try:
        r = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
        r.raise_for_status()
        tokens = r.json()
    except requests.HTTPError:
        return "Failed to authorize with Discord.", 400

    access_token = tokens.get("access_token")
    if not access_token:
        return "No access token received.", 400

    # Get user info
    user_resp = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_resp.status_code != 200:
        return "Failed to fetch user info.", 400

    session["user"] = user_resp.json()
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    """Show user dashboard with bot status and commands"""
    if "user" not in session:
        return redirect(url_for("login"))

    user = get_current_user()

    # NightWave bot commands
    commands = [
        {"name": "/play", "description": "Play a song"},
        {"name": "/nowplaying", "description": "See current song"},
        {"name": "/queue", "description": "Show the song queue"},
        {"name": "/radio", "description": "Play a radio station"},
        {"name": "/resume", "description": "Resume playback"},
        {"name": "/loop", "description": "Loop current song or queue"},
        {"name": "/leave", "description": "Make the bot leave the voice channel"},
        {"name": "/join", "description": "Make the bot join the voice channel"},
        {"name": "/invite", "description": "Get bot invite link"},
        {"name": "/bass", "description": "Adjust bass"},
        {"name": "/lyrics", "description": "Show song lyrics"},
        {"name": "/shuffle", "description": "Shuffle the queue"},
        {"name": "/skip", "description": "Skip the current song"},
        {"name": "/volume", "description": "Adjust volume"}
    ]

    bot_online = check_bot_status()
    bot_wake_up_time = get_bot_wake_up_time()

    return render_template(
        "dashboard.html",
        user=user,
        commands=commands,
        bot_online=bot_online,
        bot_wake_up_time=bot_wake_up_time
    )

@app.route("/logout")
def logout():
    """Log out user and clear session"""
    session.clear()
    return redirect(url_for("index"))

# ---------------- Run ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
