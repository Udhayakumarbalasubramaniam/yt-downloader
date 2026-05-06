import streamlit as st
import yt_dlp
import os
import base64
import tempfile
import re
import time
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
bg_css = f'url("{bg_data}")' if bg_data else "none"

# ─── CSS (Your Original UI) ──────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {{
    --surface:  rgba(10,10,18,0.84);
    --accent-yt:  #ff3c3c;
    --accent-ig:  #e1306c;
    --text:   #f0f0f0;
    --muted:  #9999bb;
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
    position: fixed; inset: 0;
    background: rgba(4,4,12,0.76);
    backdrop-filter: blur(4px);
    z-index: 0; pointer-events: none;
}}
.main .block-container {{ position: relative; z-index: 1; padding-top: 0.5rem; }}
#MainMenu, footer, header {{ visibility: hidden; }}

.title-block {{ text-align: center; padding: 2rem 0 1.2rem; }}
.title-block h1 {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem; letter-spacing: 0.08em;
    background: linear-gradient(135deg,#ff3c3c 0%,#e1306c 40%,#f77737 75%,#ffba3c 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
    filter: drop-shadow(0 0 28px rgba(225,48,108,0.45));
}}
.title-block p {{
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; margin-top: 0.4rem;
}}

.stTextInput > div > div > input {{
    background: rgba(10,10,20,0.80) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}}

.stButton > button {{
    background: linear-gradient(135deg,#e1306c,#f77737) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important; width: 100% !important;
    box-shadow: 0 4px 22px rgba(225,48,108,0.35) !important;
}}

.info-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem; margin: 0.6rem 0;
    position: relative; overflow: hidden; backdrop-filter: blur(12px);
}}
.info-card::before {{
    content:''; position:absolute; top:0; left:0; width:3px; height:100%;
    background: linear-gradient(180deg,#e1306c,#f77737);
}}

.prog-wrap {{
    background:rgba(10,10,20,0.90); border:1px solid rgba(255,255,255,0.1);
    border-radius:12px; padding:1.3rem; margin:0.8rem 0;
}}
</style>
""", unsafe_allow_html=True)

# ─── Bypass Logic ────────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_bypass_opts(is_download=False, out_tmpl=None):
    """The key fix for Streamlit Cloud 403 errors"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "no_check_certificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"], # Mimics mobile app
                "skip": ["dash", "hls"]
            }
        },
        "http_headers": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
    }
    if is_download:
        opts.update({"outtmpl": out_tmpl, "merge_output_format": "mp4"})
    return opts

# ─── UI Rendering ────────────────────────────────────────────────────────────

st.markdown("""
<div class="title-block">
  <h1>MEDIALOAD</h1>
  <p>YouTube &amp; Instagram Downloader &nbsp;·&nbsp; Video &amp; Audio</p>
</div>
""", unsafe_allow_html=True)

platform = st.radio("Platform", ["▶  YouTube", "📸  Instagram"], horizontal=True, label_visibility="collapsed")
is_instagram = "Instagram" in platform

url = st.text_input("", placeholder=f"Paste {platform.strip()} URL here...", label_visibility="collapsed")
mode = st.radio("Download as", ["🎬  Video (MP4)", "🎵  Audio (MP3)"], horizontal=True)
is_audio = "MP3" in mode

if url:
    with st.spinner("Fetching info..."):
        try:
            with yt_dlp.YoutubeDL(get_bypass_opts()) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # Show Info Card
            col1, col2 = st.columns([1, 2])
            with col1:
                thumb = info.get("thumbnail")
                if thumb: st.image(thumb, use_container_width=True)
            with col2:
                title_text = info.get("title", "Unknown Title")
                st.markdown(f"""
                <div class="info-card">
                    <h4 style="font-family:Space Mono; font-size:0.6rem; color:#999; margin:0;">TITLE</h4>
                    <p style="margin:0; font-weight:500;">{title_text[:60]}</p>
                </div>""", unsafe_allow_html=True)
            
            if st.button("⬇  DOWNLOAD NOW"):
                tmp_dir = tempfile.mkdtemp()
                title = sanitize_filename(info.get("title", "download"))
                out_tmpl = os.path.join(tmp_dir, f"{title}.%(ext)s")
                
                # Progress Placeholder
                ph = st.empty()
                ph.markdown('<div class="prog-wrap">🚀 Starting Download...</div>', unsafe_allow_html=True)

                opts = get_bypass_opts(is_download=True, out_tmpl=out_tmpl)
                
                if is_audio:
                    opts.update({
                        "format": "bestaudio/best",
                        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
                    })
                else:
                    # 'best' is more reliable than choosing a specific format ID
                    opts.update({"format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"})

                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                
                # Find file
                ext = "mp3" if is_audio else "mp4"
                file_path = None
                for f in Path(tmp_dir).iterdir():
                    if f.suffix in [f".{ext}", ".mkv", ".webm"]:
                        file_path = f
                        break

                if file_path:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    ph.empty()
                    st.success("✅ File Ready!")
                    st.download_button(
                        label=f"💾 SAVE {ext.upper()}",
                        data=data,
                        file_name=f"{title}.{ext}",
                        mime="audio/mpeg" if is_audio else "video/mp4"
                    )
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.markdown("""
    <div style="text-align:center; padding:3rem 0; opacity:0.4;">
        <p style="font-family:'Space Mono',monospace; font-size:0.7rem; text-transform:uppercase;">
            Paste a URL above to begin
        </p>
    </div>""", unsafe_allow_html=True)
