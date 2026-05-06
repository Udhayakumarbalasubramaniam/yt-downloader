import streamlit as st
import yt_dlp
import os
import base64
import tempfile
import re
import random
import shutil
from pathlib import Path
import imageio_ffmpeg

# ─────────────────────────────────────────────────────────────
# FFmpeg Fix
# ─────────────────────────────────────────────────────────────
os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# ─────────────────────────────────────────────────────────────
# Streamlit Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Media Downloader",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# Wallpaper
# ─────────────────────────────────────────────────────────────
WALLPAPER_PATH = "wallpaper.jpg"


def get_bg_base64(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()

        ext = Path(path).suffix.lower().replace(".", "")
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext

        return f"data:image/{mime};base64,{data}"

    except:
        return ""


bg_data = get_bg_base64(WALLPAPER_PATH)
bg_css = f'url("{bg_data}")' if bg_data else "none"

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&display=swap');

:root {{
    --surface: rgba(10,10,18,0.84);
    --text: #f0f0f0;
    --muted: #9999bb;
    --border: rgba(255,255,255,0.10);
}}

.stApp {{
    background-image: {bg_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp::before {{
    content: '';
    position: fixed;
    inset: 0;
    background: rgba(4,4,12,0.76);
    backdrop-filter: blur(4px);
    z-index: 0;
    pointer-events: none;
}}

.main .block-container {{
    position: relative;
    z-index: 1;
    padding-top: 0.5rem;
}}

#MainMenu, footer, header {{
    visibility: hidden;
}}

.title-block {{
    text-align: center;
    padding: 2rem 0 1.2rem;
}}

.title-block h1 {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    letter-spacing: 0.08em;

    background: linear-gradient(
        135deg,
        #ff3c3c 0%,
        #e1306c 40%,
        #f77737 75%,
        #ffba3c 100%
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    margin: 0;
    line-height: 1;

    filter: drop-shadow(0 0 28px rgba(225,48,108,0.45));
}}

.title-block p {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}}

.stTextInput > div > div > input {{
    background: rgba(10,10,20,0.80) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}}

.stButton > button {{
    background: linear-gradient(135deg,#e1306c,#f77737) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important;
    width: 100% !important;
    box-shadow: 0 4px 22px rgba(225,48,108,0.35) !important;
}}

.info-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.6rem 0;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}}

.prog-wrap {{
    background: rgba(10,10,20,0.90);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.3rem;
    margin: 0.8rem 0;
}}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


# IMPORTANT FIX
# This avoids most Streamlit Cloud 403 errors

def get_ydl_opts(download=False, outtmpl=None):

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
    ]

    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "http_headers": {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9",
        },

        # MAIN FIX
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }

    if download:
        opts["outtmpl"] = outtmpl
        opts["merge_output_format"] = "mp4"

    return opts


# ─────────────────────────────────────────────────────────────
# Title
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>MEDIALOAD</h1>
    <p>YOUTUBE · INSTAGRAM · VIDEO · AUDIO</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────
url = st.text_input(
    "",
    placeholder="Paste YouTube or Instagram URL...",
    label_visibility="collapsed"
)

# ─────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────
if "formats" not in st.session_state:
    st.session_state.formats = None

if "info" not in st.session_state:
    st.session_state.info = None

# ─────────────────────────────────────────────────────────────
# Fetch Button
# ─────────────────────────────────────────────────────────────
if st.button("📥 FETCH VIDEO INFO"):

    if not url:
        st.warning("Please enter a URL")
        st.stop()

    try:

        with st.spinner("Fetching video info..."):

            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                info = ydl.extract_info(url, download=False)

            st.session_state.info = info

            formats = []

            seen = set()

            for f in info.get("formats", []):

                if f.get("vcodec") == "none":
                    continue

                if f.get("height") is None:
                    continue

                resolution = f"{f.get('height')}p"

                ext = f.get("ext", "mp4")

                filesize = f.get("filesize") or f.get("filesize_approx")

                if filesize:
                    filesize = round(filesize / (1024 * 1024), 2)
                    size_text = f"{filesize} MB"
                else:
                    size_text = "Unknown"

                label = f"{resolution} | {ext.upper()} | {size_text}"

                if label in seen:
                    continue

                seen.add(label)

                formats.append({
                    "label": label,
                    "id": f["format_id"]
                })

            formats = sorted(
                formats,
                key=lambda x: int(x["label"].split("p")[0]),
                reverse=True
            )

            st.session_state.formats = formats

    except Exception as e:
        st.error(f"Error: {e}")

# ─────────────────────────────────────────────────────────────
# Video Info
# ─────────────────────────────────────────────────────────────
if st.session_state.info:

    info = st.session_state.info

    col1, col2 = st.columns([1, 2])

    with col1:
        if info.get("thumbnail"):
            st.image(info["thumbnail"], use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4 style="font-family:Space Mono;
                       font-size:0.6rem;
                       color:#999;
                       margin:0;">
                TITLE
            </h4>

            <p style="margin:0;
                      font-weight:500;">
                {info.get("title")}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Quality Selector
# ─────────────────────────────────────────────────────────────
if st.session_state.formats:

    labels = [x["label"] for x in st.session_state.formats]

    selected = st.selectbox(
        "Choose Quality",
        labels
    )

    mode = st.radio(
        "Download Type",
        ["🎬 Video MP4", "🎵 Audio MP3"],
        horizontal=True
    )

    # ─────────────────────────────────────────────────────────
    # Download
    # ─────────────────────────────────────────────────────────
    if st.button("⬇ DOWNLOAD NOW"):

        try:

            progress = st.empty()

            progress.markdown("""
            <div class="prog-wrap">
                🚀 Download Started...
            </div>
            """, unsafe_allow_html=True)

            selected_format = next(
                x for x in st.session_state.formats
                if x["label"] == selected
            )

            format_id = selected_format["id"]

            tmp_dir = tempfile.mkdtemp()

            title = sanitize_filename(
                st.session_state.info.get("title", "download")
            )

            outtmpl = os.path.join(
                tmp_dir,
                f"{title}.%(ext)s"
            )

            opts = get_ydl_opts(
                download=True,
                outtmpl=outtmpl
            )

            # AUDIO
            if "Audio" in mode:

                opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]
                })

            # VIDEO
            else:

                # MAIN 403 FIX
                # Avoid DASH merging
                opts.update({
                    "format": format_id
                })

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            files = list(Path(tmp_dir).glob("*"))

            file_path = None

            for f in files:

                if "Audio" in mode:
                    if f.suffix.lower() in [".mp3", ".m4a"]:
                        file_path = f
                        break
                else:
                    if f.suffix.lower() in [".mp4", ".mkv", ".webm"]:
                        file_path = f
                        break

            if not file_path:
                st.error("Download failed")
                st.stop()

            with open(file_path, "rb") as f:
                data = f.read()

            progress.empty()

            st.success("✅ Download Ready!")

            st.download_button(
                label="💾 SAVE FILE",
                data=data,
                file_name=file_path.name,
                mime=(
                    "audio/mpeg"
                    if "Audio" in mode
                    else "video/mp4"
                )
            )

            # Cleanup
            try:
                shutil.rmtree(tmp_dir)
            except:
                pass

        except Exception as e:
            st.error(f"Download Error: {e}")

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────
if not url:

    st.markdown("""
    <div style="text-align:center;
                padding:3rem 0;
                opacity:0.4;">

        <p style="font-family:'Space Mono',monospace;
                  font-size:0.7rem;
                  text-transform:uppercase;">

            Paste a URL above to begin

        </p>

    </div>
    """, unsafe_allow_html=True)

