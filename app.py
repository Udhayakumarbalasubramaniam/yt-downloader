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
    page_title="MEDIALOAD",
    page_icon="🎬",
    layout="centered",
)

# ─── CSS (Simplified & Fixed) ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono&family=Bebas+Neue&family=DM+Sans:wght@400;500&display=swap');

:root {
    --accent: #ff3c3c;
    --bg-dark: #0a0a12;
}

.stApp {
    background-color: var(--bg-dark);
    color: #f0f0f0;
}

.title-block {
    text-align: center;
    padding: 2rem 0;
}

.title-block h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    background: linear-gradient(135deg, #ff3c3c, #e1306c, #f77737);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.info-card {
    background: rgba(255,255,255,0.05);
    border-left: 3px solid var(--accent);
    padding: 1rem;
    border-radius: 5px;
    margin: 10px 0;
}

.prog-wrap {
    background: #1a1a2e;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)

# ─── Logic Helpers ──────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_ydl_opts(is_download=False, out_tmpl=None, ph=None, bar_type="yt"):
    """
    Core configuration to bypass Streamlit Cloud blocks.
    Uses Android/Web clients to mimic real device traffic.
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        "no_check_certificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "skip": ["dash", "hls"]
            }
        },
        "http_headers": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }
    
    if is_download:
        opts.update({
            "outtmpl": out_tmpl,
            "progress_hooks": [progress_hook_factory(ph, bar_type)],
            "merge_output_format": "mp4",
        })
    return opts

def progress_hook_factory(ph, bar_type):
    def hook(d):
        if d["status"] == "downloading":
            p = d.get("_percent_str", "0%").replace("%", "")
            try:
                pct = float(p)
            except:
                pct = 0.0
            spd = d.get("_speed_str", "N/A")
            ph.markdown(f"**Downloading:** {pct}% | Speed: {spd}")
        elif d["status"] == "finished":
            ph.markdown("**Status:** Finalizing file...")
    return hook

# ─── Main App ────────────────────────────────────────────────────────────────

st.markdown('<div class="title-block"><h1>MEDIALOAD</h1><p>NO-COOKIE BYPASS MODE</p></div>', unsafe_allow_html=True)

platform = st.radio("Select Platform", ["YouTube", "Instagram"], horizontal=True)
url = st.text_input("Paste URL here", placeholder="https://...")
mode = st.radio("Format", ["Video (MP4)", "Audio (MP3)"], horizontal=True)

if url:
    with st.spinner("Bypassing filters and fetching metadata..."):
        try:
            # We don't use cookies here to mimic 'offline' behavior via header spoofing
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                info = ydl.extract_info(url, download=False)
                
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(info.get("thumbnail", ""))
            with col2:
                st.markdown(f"""
                <div class="info-card">
                    <b>Title:</b> {info.get('title', 'Unknown')[:60]}...<br>
                    <b>Duration:</b> {info.get('duration', 0) // 60} min<br>
                    <b>Uploader:</b> {info.get('uploader', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

            if st.button("⬇️ START DOWNLOAD"):
                tmp_dir = tempfile.mkdtemp()
                title = sanitize_filename(info.get('title', 'video'))
                out_tmpl = os.path.join(tmp_dir, f"{title}.%(ext)s")
                ph = st.empty()
                
                download_opts = get_ydl_opts(is_download=True, out_tmpl=out_tmpl, ph=ph)
                
                if "MP3" in mode:
                    download_opts.update({
                        "format": "bestaudio/best",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                    })
                else:
                    # 'best' is safer for bypass than specific IDs
                    download_opts.update({"format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"})

                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    ydl.download([url])
                
                # Find the resulting file
                ext = "mp3" if "MP3" in mode else "mp4"
                downloaded_file = None
                for f in Path(tmp_dir).iterdir():
                    if f.suffix in [f".{ext}", ".mkv", ".webm"]:
                        downloaded_file = f
                        break
                
                if downloaded_file:
                    with open(downloaded_file, "rb") as f:
                        st.download_button(
                            label=f"💾 SAVE {ext.upper()}",
                            data=f,
                            file_name=f"{title}.{ext}",
                            mime=f"audio/mpeg" if ext == "mp3" else "video/mp4",
                            use_container_width=True
                        )
                    st.success("Download Successful!")
                else:
                    st.error("File processing failed. Please try again.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("YouTube sometimes blocks Cloud IPs. If this persists, the server IP is temporary blacklisted.")

else:
    st.info("Ready. Enter a link above to start.")
