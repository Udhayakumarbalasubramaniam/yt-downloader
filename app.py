import streamlit as st
import yt_dlp
import os
import base64
import tempfile
import re
import time
import json
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Media Downloader",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Wallpaper Background ────────────────────────────────────────────────────
WALLPAPER_PATH = "wallpaper.jpg"

def get_bg_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = Path(path).suffix.lower().replace(".", "")
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        return f"data:image/{mime};base64,{data}"
    except Exception:
        return ""

bg_data = get_bg_base64(WALLPAPER_PATH)
bg_css  = f'url("{bg_data}")' if bg_data else "none"

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {{
    --surface:  rgba(10,10,18,0.84);
    --surface2: rgba(20,20,32,0.90);
    --accent-yt:  #ff3c3c;
    --accent-ig:  #e1306c;
    --accent-ig2: #f77737;
    --accent-mp3: #a78bfa;
    --text:   #f0f0f0;
    --muted:  #9999bb;
    --border: rgba(255,255,255,0.10);
}}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}}

/* ── WALLPAPER ── */
.stApp {{
    background-image: {bg_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background: rgba(4,4,12,0.76);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 0; pointer-events: none;
}}
.main .block-container {{
    position: relative; z-index: 1;
    padding-top: 0.5rem;
}}
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── TITLE ── */
.title-block {{
    text-align: center;
    padding: 2rem 0 1.2rem;
}}
.title-block h1 {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem; letter-spacing: 0.08em;
    background: linear-gradient(135deg,#ff3c3c 0%,#e1306c 40%,#f77737 75%,#ffba3c 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0; line-height: 1;
    filter: drop-shadow(0 0 28px rgba(225,48,108,0.45));
}}
.title-block p {{
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; margin-top: 0.4rem;
}}

/* ── INPUT ── */
.stTextInput > div > div > input {{
    background: rgba(10,10,20,0.80) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.83rem !important; padding: 0.75rem 1rem !important;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.stTextInput > div > div > input:focus {{
    border-color: var(--accent-ig) !important;
    box-shadow: 0 0 0 1px var(--accent-ig), 0 0 18px rgba(225,48,108,0.2) !important;
}}
.stTextInput > div > div > input::placeholder {{ color: #44445566 !important; }}

/* ── RADIO ── */
.stRadio > div {{ flex-direction: row !important; gap: 1rem; }}
.stRadio label {{
    font-family: 'Space Mono', monospace !important;
    font-size: 0.76rem !important; color: var(--muted) !important;
}}

/* ── SELECT ── */
.stSelectbox > div > div {{
    background: rgba(10,10,20,0.80) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 8px !important; color: var(--text) !important;
    backdrop-filter: blur(8px);
}}

/* ── BUTTONS ── */
.stButton > button {{
    background: linear-gradient(135deg,#e1306c,#f77737) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important; letter-spacing: 0.12em !important;
    padding: 0.65rem 2.5rem !important; width: 100% !important;
    box-shadow: 0 4px 22px rgba(225,48,108,0.35) !important;
    transition: opacity 0.2s, transform 0.15s !important;
}}
.stButton > button:hover  {{ opacity:0.88 !important; transform:translateY(-2px) !important; }}
.stButton > button:active {{ transform:translateY(0) !important; }}

/* ── SAVE BTN ── */
.stDownloadButton > button {{
    background: linear-gradient(135deg,#3cffa0,#3ce0ff) !important;
    color: #06060f !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important; letter-spacing: 0.12em !important;
    padding: 0.65rem 2.5rem !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(60,255,160,0.3) !important;
}}

/* ── INFO CARDS ── */
.info-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem 1.3rem; margin: 0.6rem 0;
    position: relative; overflow: hidden; backdrop-filter: blur(12px);
}}
.info-card::before {{
    content:''; position:absolute; top:0; left:0;
    width:3px; height:100%;
    background: linear-gradient(180deg,#e1306c,#f77737);
}}
.info-card.yt::before  {{ background:linear-gradient(180deg,#ff3c3c,#ff7a3c); }}
.info-card.mp3::before {{ background:linear-gradient(180deg,#a78bfa,#818cf8); }}
.info-card.lock::before {{ background:linear-gradient(180deg,#facc15,#f97316); }}
.info-card h4 {{
    font-family:'Space Mono',monospace; font-size:0.63rem;
    text-transform:uppercase; letter-spacing:0.18em;
    color:var(--muted); margin:0 0 0.2rem;
}}
.info-card p {{ font-size:0.92rem; font-weight:500; margin:0; color:var(--text); }}

/* ── THUMBNAIL ── */
.thumb-wrap {{
    border-radius:10px; overflow:hidden; border:1px solid var(--border);
    box-shadow:0 8px 32px rgba(0,0,0,0.55); margin-bottom:0.8rem;
}}
.thumb-wrap img {{ width:100%; display:block; }}

/* ── DIVIDER ── */
.divider {{ border:none; border-top:1px solid rgba(255,255,255,0.07); margin:1rem 0; }}

/* ── MODE BADGE ── */
.mode-badge {{
    display:inline-block; padding:0.18rem 0.7rem; border-radius:4px;
    font-family:'Space Mono',monospace; font-size:0.66rem;
    font-weight:700; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.7rem;
}}
.mode-badge.yt    {{ background:rgba(255,60,60,0.15);   color:#ff9090; border:1px solid rgba(255,60,60,0.35); }}
.mode-badge.ig    {{ background:rgba(225,48,108,0.15);  color:#f780a8; border:1px solid rgba(225,48,108,0.35); }}
.mode-badge.audio {{ background:rgba(167,139,250,0.15); color:#c4b5fd; border:1px solid rgba(167,139,250,0.35); }}
.mode-badge.lock  {{ background:rgba(250,204,21,0.15);  color:#fde68a; border:1px solid rgba(250,204,21,0.35); }}

/* ── IG NOTE ── */
.ig-note {{
    background:rgba(225,48,108,0.10); border:1px solid rgba(225,48,108,0.25);
    border-radius:8px; padding:0.8rem 1rem;
    font-family:'Space Mono',monospace; font-size:0.68rem;
    color:#f780a8; line-height:1.6; margin-bottom:0.8rem;
}}

/* ── PRIVATE LOGIN BOX ── */
.login-box {{
    background: rgba(250,204,21,0.06);
    border: 1px solid rgba(250,204,21,0.25);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 0.8rem 0;
    backdrop-filter: blur(12px);
}}
.login-box h3 {{
    font-family:'Bebas Neue',sans-serif;
    font-size:1.1rem; letter-spacing:0.12em;
    color:#fde68a; margin:0 0 0.6rem;
}}
.login-box p {{
    font-family:'Space Mono',monospace;
    font-size:0.66rem; color:#9999bb; line-height:1.6; margin:0 0 0.8rem;
}}

/* ── TAB / METHOD PILLS ── */
.method-pills {{
    display:flex; gap:0.5rem; margin-bottom:1rem;
}}
.pill {{
    flex:1; padding:0.5rem 0.8rem; border-radius:6px;
    font-family:'Space Mono',monospace; font-size:0.68rem;
    letter-spacing:0.1em; text-align:center; cursor:pointer;
    border:1px solid var(--border); color:var(--muted);
    background:var(--surface); transition:all 0.2s;
}}
.pill.active {{
    background:rgba(250,204,21,0.12);
    border-color:rgba(250,204,21,0.4);
    color:#fde68a;
}}

/* ── ALERT ── */
.stAlert {{ background:rgba(10,10,20,0.84)!important; border-radius:8px!important; backdrop-filter:blur(8px)!important; }}

label {{
    color:var(--muted)!important;
    font-family:'Space Mono',monospace!important;
    font-size:0.7rem!important; text-transform:uppercase; letter-spacing:0.1em;
}}

/* ── FILE UPLOADER ── */
.stFileUploader {{
    background: rgba(10,10,20,0.80) !important;
    border: 1px dashed rgba(250,204,21,0.35) !important;
    border-radius: 8px !important;
}}

/* ══════════════════════════════
   ANIMATED PROGRESS BAR
══════════════════════════════ */
.prog-wrap {{
    background:rgba(10,10,20,0.90); border:1px solid rgba(255,255,255,0.1);
    border-radius:12px; padding:1.3rem 1.5rem; margin:0.8rem 0;
    backdrop-filter:blur(16px);
}}
.prog-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; }}
.prog-label {{
    font-family:'Space Mono',monospace; font-size:0.7rem;
    text-transform:uppercase; letter-spacing:0.15em; color:var(--muted);
}}
.prog-pct {{
    font-family:'Bebas Neue',sans-serif; font-size:1.6rem;
    letter-spacing:0.05em; color:var(--text); line-height:1;
}}
.prog-pct span {{ font-size:0.85rem; color:var(--muted); }}
.prog-track {{
    width:100%; height:8px; background:rgba(255,255,255,0.07);
    border-radius:999px; overflow:hidden; position:relative;
}}
.prog-bar {{
    height:100%; border-radius:999px;
    background:linear-gradient(90deg,#ff3c3c,#e1306c,#f77737,#ffba3c);
    background-size:300% 100%;
    transition:width 0.35s cubic-bezier(0.4,0,0.2,1);
    position:relative; animation:shimmer 1.8s linear infinite;
}}
.prog-bar.ig  {{ background:linear-gradient(90deg,#833ab4,#e1306c,#f77737,#fcaf45); background-size:300% 100%; }}
.prog-bar.mp3 {{ background:linear-gradient(90deg,#a78bfa,#818cf8,#60a5fa); background-size:300% 100%; }}
@keyframes shimmer {{ 0%{{background-position:300% 0}} 100%{{background-position:-300% 0}} }}
.prog-bar::after {{
    content:''; position:absolute; right:-2px; top:50%; transform:translateY(-50%);
    width:13px; height:13px; border-radius:50%; background:#fff;
    box-shadow:0 0 10px rgba(255,100,60,0.9);
}}
.prog-bar.ig::after  {{ box-shadow:0 0 12px rgba(225,48,108,0.9); }}
.prog-bar.mp3::after {{ box-shadow:0 0 10px rgba(167,139,250,0.9); }}
.prog-speed {{
    font-family:'Space Mono',monospace; font-size:0.66rem;
    color:var(--muted); margin-top:0.45rem; min-height:1rem;
}}
@keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:0.35;transform:scale(0.65)}} }}
.live-dot {{
    display:inline-block; width:7px; height:7px; border-radius:50%;
    background:#e1306c; margin-right:6px; vertical-align:middle;
    animation:pulse 1s ease-in-out infinite;
}}
.live-dot.yt  {{ background:#ff3c3c; }}
.live-dot.mp3 {{ background:#a78bfa; }}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def fetch_video_info(url: str, cookies_file: str = None, username: str = None, password: str = None):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file
    if username and password:
        ydl_opts["username"] = username
        ydl_opts["password"] = password
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def get_video_formats(info: dict):
    seen = {}
    for f in info.get("formats", []):
        height = f.get("height")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        if not height or vcodec == "none":
            continue
        ext    = f.get("ext", "")
        fps    = f.get("fps") or ""
        fps_str = f" {int(fps)}fps" if fps else ""
        label  = f"{height}p{fps_str} ({ext.upper()})"
        if height not in seen or (acodec != "none" and seen[height][2] == "none"):
            seen[height] = (label, f["format_id"], acodec, ext)
    return [(v[0], v[1]) for _, v in sorted(seen.items(), reverse=True)]

# ─── Progress ────────────────────────────────────────────────────────────────

def render_progress(ph, pct: float, speed_str: str, bar_type: str, status: str):
    pct = max(0.0, min(100.0, pct))
    dot_class = f"live-dot {bar_type}" if bar_type in ("yt","mp3") else "live-dot"
    bar_class  = f"prog-bar {bar_type}" if bar_type in ("ig","mp3") else "prog-bar"
    ph.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-header">
            <div class="prog-label"><span class="{dot_class}"></span>{status}</div>
            <div class="prog-pct">{pct:.1f}<span>%</span></div>
        </div>
        <div class="prog-track">
            <div class="{bar_class}" style="width:{pct}%"></div>
        </div>
        <div class="prog-speed">{speed_str}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_hook_factory(ph, bar_type):
    state = {"pct": 0.0}
    def hook(d):
        if d["status"] == "downloading":
            raw = re.sub(r'\x1b\[[0-9;]*m', '', d.get("_percent_str","0%").strip())
            try:    pct = float(raw.replace("%","").strip())
            except: pct = state["pct"]
            spd = re.sub(r'\x1b\[[0-9;]*m', '', d.get("_speed_str","").strip())
            eta = re.sub(r'\x1b\[[0-9;]*m', '', d.get("_eta_str","").strip())
            info_str = f"⚡ {spd}" + (f"  ·  ETA {eta}" if eta else "")
            state["pct"] = pct
            render_progress(ph, pct, info_str, bar_type, "Downloading")
        elif d["status"] == "finished":
            render_progress(ph, 100.0, "⚙️  Merging / Converting…", bar_type, "Processing")
    return hook

# ─── Download functions ──────────────────────────────────────────────────────

def _base_ig_opts(out_tmpl, ph, cookies_file=None, username=None, password=None):
    opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": out_tmpl,
        "quiet": False, "no_warnings": True,
        "merge_output_format": "mp4",
        "postprocessors": [{"key":"FFmpegVideoConvertor","preferedformat":"mp4"}],
        "progress_hooks": [progress_hook_factory(ph, "ig")],
    }
    if cookies_file:
        opts["cookiefile"] = cookies_file
    if username and password:
        opts["username"] = username
        opts["password"] = password
    return opts

def download_video(url, format_id, out_dir, title, ph, bar_type, cookies_file=None):
    fname    = sanitize_filename(title)
    out_tmpl = os.path.join(out_dir, f"{fname}.%(ext)s")
    opts = {
        "format": f"{format_id}+bestaudio/best",
        "outtmpl": out_tmpl, "quiet": False, "no_warnings": True,
        "merge_output_format": "mp4",
        "postprocessors": [{"key":"FFmpegVideoConvertor","preferedformat":"mp4"}],
        "progress_hooks": [progress_hook_factory(ph, bar_type)],
    }
    if cookies_file:
        opts["cookiefile"] = cookies_file
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    for f in Path(out_dir).iterdir():
        if f.suffix == ".mp4": return str(f)
    raise FileNotFoundError("MP4 not found after download.")

def download_audio(url, out_dir, title, ph, bar_type,
                   cookies_file=None, username=None, password=None):
    fname    = sanitize_filename(title)
    out_tmpl = os.path.join(out_dir, f"{fname}.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl, "quiet": False, "no_warnings": True,
        "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"320"}],
        "progress_hooks": [progress_hook_factory(ph, bar_type)],
    }
    if cookies_file: opts["cookiefile"] = cookies_file
    if username and password:
        opts["username"] = username
        opts["password"] = password
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    for f in Path(out_dir).iterdir():
        if f.suffix == ".mp3": return str(f)
    raise FileNotFoundError("MP3 not found after download.")

def download_instagram(url, out_dir, title, ph,
                       cookies_file=None, username=None, password=None):
    fname    = sanitize_filename(title or "instagram_video")
    out_tmpl = os.path.join(out_dir, f"{fname}.%(ext)s")
    opts     = _base_ig_opts(out_tmpl, ph, cookies_file, username, password)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    for f in Path(out_dir).iterdir():
        if f.suffix == ".mp4": return str(f)
    raise FileNotFoundError("Instagram video not found after download.")

# ─── Session state defaults ───────────────────────────────────────────────────
if "ig_method"   not in st.session_state: st.session_state.ig_method   = "public"
if "ig_user"     not in st.session_state: st.session_state.ig_user     = ""
if "ig_pass"     not in st.session_state: st.session_state.ig_pass     = ""
if "cookie_path" not in st.session_state: st.session_state.cookie_path = None

# ─── UI ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="title-block">
  <h1>MEDIALOAD</h1>
  <p>YouTube &amp; Instagram Downloader &nbsp;·&nbsp; Video &amp; Audio</p>
</div>
""", unsafe_allow_html=True)

# ── Platform selector ──
platform     = st.radio("Platform", ["▶  YouTube", "📸  Instagram"],
                        horizontal=True, label_visibility="collapsed")
is_instagram = "Instagram" in platform

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# YOUTUBE COOKIE PANEL  (fixes 403 on Streamlit Cloud)
# ─────────────────────────────────────────────────────────────────────────────
yt_cookies_file = None

if not is_instagram:
    with st.expander("🍪  YouTube Cookie Login  (required on Streamlit Cloud)", expanded=False):
        st.markdown("""
        <div class="login-box">
            <h3>🍪 Fix YouTube 403 Error</h3>
            <p>
            Streamlit Cloud servers get blocked by YouTube.<br>
            Upload your browser cookies so yt-dlp looks like your real browser.<br><br>
            <b>How to get cookies.txt in 3 steps:</b><br>
            1. Install extension: <b>Get cookies.txt LOCALLY</b> (Chrome / Firefox)<br>
            2. Open <b>youtube.com</b> while logged in to your Google account<br>
            3. Click extension → <b>Export cookies for youtube.com</b> → upload below
            </p>
        </div>
        """, unsafe_allow_html=True)

        yt_uploaded = st.file_uploader(
            "Upload YouTube cookies.txt", type=["txt"],
            key="yt_cookie_uploader",
            help="Netscape format cookie file exported from your browser"
        )
        if yt_uploaded is not None:
            yt_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb")
            yt_tmp.write(yt_uploaded.read())
            yt_tmp.flush()
            yt_tmp.close()
            st.session_state["yt_cookie_path"] = yt_tmp.name
            yt_cookies_file = yt_tmp.name
            st.success("✅  YouTube cookies loaded — 403 errors bypassed!")
        elif st.session_state.get("yt_cookie_path") and Path(st.session_state["yt_cookie_path"]).exists():
            yt_cookies_file = st.session_state["yt_cookie_path"]
            st.success("✅  Using previously uploaded YouTube cookies.")
        else:
            st.warning("⚠️  No cookies yet — uploads may fail with 403. Please upload cookies.txt above.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INSTAGRAM PANEL
# ─────────────────────────────────────────────────────────────────────────────
cookies_file = None
ig_username  = None
ig_password  = None

if is_instagram:
    st.markdown("""
    <div class="ig-note">
        📌 &nbsp;Supports: <b>Reels · Posts · IGTV · Stories · Highlights</b><br>
        🌐 &nbsp;Public posts work instantly — no login needed.<br>
        🔒 &nbsp;Private accounts: use one of the login methods below.
    </div>
    """, unsafe_allow_html=True)

    # ── Login method toggle ──
    method_col1, method_col2, method_col3 = st.columns(3)
    with method_col1:
        if st.button("🌐  Public", use_container_width=True):
            st.session_state.ig_method = "public"
    with method_col2:
        if st.button("🔑  Username / Password", use_container_width=True):
            st.session_state.ig_method = "userpass"
    with method_col3:
        if st.button("🍪  Cookie File", use_container_width=True):
            st.session_state.ig_method = "cookie"

    method = st.session_state.ig_method

    # ── Active method indicator ──
    method_labels = {
        "public":  ("🌐 PUBLIC MODE",   "No login required — works only for public posts."),
        "userpass":("🔑 PASSWORD LOGIN","Enter your Instagram credentials below."),
        "cookie":  ("🍪 COOKIE LOGIN",  "Upload a Netscape cookies.txt file exported from your browser."),
    }
    lbl, desc = method_labels[method]
    st.markdown(f"""
    <div class="info-card lock" style="margin-bottom:0.5rem;">
        <h4>{lbl}</h4><p style="font-size:0.8rem; color:#ccc;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Username / Password fields ──
    if method == "userpass":
        st.markdown("""
        <div class="login-box">
            <h3>🔐 Instagram Login</h3>
            <p>Your credentials are used only locally by yt-dlp to fetch the session.<br>
               They are <b>never stored</b> or sent anywhere else.</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            ig_username = st.text_input("Instagram Username", value=st.session_state.ig_user,
                                        placeholder="your_username")
            st.session_state.ig_user = ig_username
        with c2:
            ig_password = st.text_input("Instagram Password", value=st.session_state.ig_pass,
                                        placeholder="••••••••", type="password")
            st.session_state.ig_pass = ig_password

        if ig_username and ig_password:
            st.success(f"✅  Logged in as **{ig_username}** — private posts accessible.")
        else:
            st.warning("Enter both username and password to access private posts.")

    # ── Cookie file upload ──
    elif method == "cookie":
        st.markdown("""
        <div class="login-box">
            <h3>🍪 How to get cookies.txt</h3>
            <p>
            1. Install browser extension: <b>Get cookies.txt LOCALLY</b> (Chrome/Firefox)<br>
            2. Log in to Instagram in your browser<br>
            3. Click the extension → Export cookies for instagram.com<br>
            4. Upload the downloaded <b>cookies.txt</b> file below
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_cookie = st.file_uploader(
            "Upload cookies.txt", type=["txt"],
            help="Netscape format cookie file from your browser"
        )

        if uploaded_cookie is not None:
            # Save to a temp file that persists for this session
            cookie_tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt", mode="wb"
            )
            cookie_tmp.write(uploaded_cookie.read())
            cookie_tmp.flush()
            cookie_tmp.close()
            st.session_state.cookie_path = cookie_tmp.name
            cookies_file = cookie_tmp.name
            st.success("✅  Cookie file loaded — private posts accessible.")
        elif st.session_state.cookie_path and Path(st.session_state.cookie_path).exists():
            cookies_file = st.session_state.cookie_path
            st.success("✅  Using previously uploaded cookie file.")
        else:
            st.warning("Upload a cookies.txt file to access private posts.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── URL input ──
placeholder_text = "Paste Instagram URL here…" if is_instagram else "Paste YouTube URL here…"
url = st.text_input("", placeholder=placeholder_text, label_visibility="collapsed")

# ── Mode ──
mode     = st.radio("Download as", ["🎬  Video (MP4)", "🎵  Audio (MP3)"], horizontal=True)
is_audio = "MP3" in mode

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Fetch info ──
info    = None
formats = []

if url:
    with st.spinner("Fetching info…"):
        try:
            info = fetch_video_info(
                url,
                cookies_file=cookies_file if is_instagram else yt_cookies_file,
                username=ig_username if is_instagram else None,
                password=ig_password if is_instagram else None,
            )
            formats = get_video_formats(info)
        except Exception as e:
            err = str(e)
            st.error(f"Could not fetch info: {err}")
            if "login" in err.lower() or "private" in err.lower() or "403" in err:
                st.info("🔒 This looks like a private post. Switch to **Password** or **Cookie** login above.")

if info:
    col1, col2 = st.columns([1, 2])
    with col1:
        thumb = info.get("thumbnail")
        if thumb:
            st.markdown(f'<div class="thumb-wrap"><img src="{thumb}"/></div>', unsafe_allow_html=True)
    with col2:
        if is_audio:
            badge_cls, badge_lbl = "audio", "MP3 AUDIO"
        elif is_instagram:
            badge_cls, badge_lbl = "ig", "INSTAGRAM"
        else:
            badge_cls, badge_lbl = "yt", "YOUTUBE"

        st.markdown(f'<span class="mode-badge {badge_cls}">{badge_lbl}</span>', unsafe_allow_html=True)

        card_cls = "mp3" if is_audio else ("ig" if is_instagram else "yt")
        title_text = info.get("title") or (info.get("description","Untitled")[:55] + "…")
        st.markdown(f"""
        <div class="info-card {card_cls}">
            <h4>Title</h4><p>{title_text}</p>
        </div>""", unsafe_allow_html=True)

        dur     = info.get("duration")
        dur_str = f"{int(dur)//60}:{int(dur)%60:02d}" if dur else "—"
        owner   = info.get("uploader") or info.get("channel") or "—"
        c1, c2  = st.columns(2)
        with c1:
            st.markdown(f"""<div class="info-card {card_cls}"><h4>Duration</h4><p>{dur_str}</p></div>""",
                        unsafe_allow_html=True)
        with c2:
            lbl2 = "Account" if is_instagram else "Channel"
            st.markdown(f"""<div class="info-card {card_cls}"><h4>{lbl2}</h4><p>{owner}</p></div>""",
                        unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Quality selector ──
    selected_format_id = "bestvideo+bestaudio/best"
    bar_type = "mp3" if is_audio else ("ig" if is_instagram else "yt")

    if not is_audio and not is_instagram:
        if formats:
            quality_labels     = [f[0] for f in formats]
            choice             = st.selectbox("Select Quality", quality_labels)
            selected_format_id = dict(formats)[choice]
        else:
            st.warning("No formats found — will use best available.")
    elif not is_audio and is_instagram:
        st.markdown("""<div class="info-card ig"><h4>Quality</h4>
            <p>Best Available (auto)</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="info-card mp3"><h4>Audio Quality</h4>
            <p>320 kbps MP3 &nbsp;·&nbsp; Best Available</p></div>""", unsafe_allow_html=True)

    # ── Download ──
    if st.button("⬇  DOWNLOAD NOW"):
        tmp_dir    = tempfile.mkdtemp()
        title      = info.get("title") or (info.get("description","download")[:40])
        ph         = st.empty()
        render_progress(ph, 0.0, "Initializing…", bar_type, "Starting")

        try:
            if is_audio:
                file_path = download_audio(
                    url, tmp_dir, title, ph, bar_type,
                    cookies_file=cookies_file if is_instagram else yt_cookies_file,
                    username=ig_username if is_instagram else None,
                    password=ig_password if is_instagram else None,
                )
                mime    = "audio/mpeg"
                dl_name = sanitize_filename(title) + ".mp3"
            elif is_instagram:
                file_path = download_instagram(
                    url, tmp_dir, title, ph,
                    cookies_file=cookies_file,
                    username=ig_username,
                    password=ig_password,
                )
                mime    = "video/mp4"
                dl_name = sanitize_filename(title) + ".mp4"
            else:
                file_path = download_video(url, selected_format_id, tmp_dir, title, ph, bar_type,
                                            cookies_file=yt_cookies_file)
                mime      = "video/mp4"
                dl_name   = sanitize_filename(title) + ".mp4"

            render_progress(ph, 100.0, "✅  Complete!", bar_type, "Done")
            time.sleep(0.5)
            ph.empty()

            with open(file_path, "rb") as f:
                data = f.read()

            st.success("✅  File ready — click below to save!")
            st.download_button(
                label=f"💾  SAVE  {'MP3' if is_audio else 'MP4'}",
                data=data, file_name=dl_name, mime=mime,
            )

        except Exception as e:
            ph.empty()
            err = str(e)
            st.error(f"Download failed: {err}")
            if "login" in err.lower() or "403" in err or "private" in err.lower():
                st.warning("🔒 Private post detected! Use the **Password** or **Cookie** login method above.")
            else:
                st.info("Make sure ffmpeg is installed:  sudo apt install ffmpeg")

else:
    if not url:
        icon = "📸" if is_instagram else "▶"
        label_txt = "Instagram" if is_instagram else "YouTube"
        st.markdown(f"""
        <div style="text-align:center; padding:3rem 0;">
            <div style="font-size:3rem; margin-bottom:0.8rem; opacity:0.4;">{icon}</div>
            <p style="font-family:'Space Mono',monospace; font-size:0.72rem;
                      letter-spacing:0.18em; text-transform:uppercase; color:#44445688;">
                Paste a {label_txt} URL above to begin
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
  <p style="font-family:'Space Mono',monospace; font-size:0.6rem;
            letter-spacing:0.15em; color:#333355;">
    POWERED BY YT-DLP + FFMPEG &nbsp;·&nbsp; POP OS 22
  </p>
</div>
""", unsafe_allow_html=True)
