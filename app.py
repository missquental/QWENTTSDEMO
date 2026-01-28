import streamlit as st
import subprocess
import os
import threading
import time
import requests
from pathlib import Path

# Konfigurasi halaman
st.set_page_config(
    page_title="Qwen TTS Generator",
    page_icon="🎙️",
    layout="wide"
)

# Fungsi untuk menjalankan instalasi (hanya sekali)
def install_dependencies():
    if not os.path.exists("install_done.flag"):
        with st.spinner("Installing dependencies... This may take a few minutes."):
            try:
                # Update system
                subprocess.run("apt update", shell=True, check=True)
                
                # Install ffmpeg
                subprocess.run("apt install -y ffmpeg", shell=True, check=True)
                
                # Install qwen-tts
                subprocess.run("pip install -U qwen-tts", shell=True, check=True)
                
                # Install flash-attn
                subprocess.run("pip install flash-attn --no-build-isolation", shell=True, check=True)
                
                # Buat flag file
                Path("install_done.flag").touch()
                st.success("Installation completed!")
            except Exception as e:
                st.error(f"Installation failed: {str(e)}")
                return False
    return True

# Fungsi untuk menjalankan server TTS
def start_tts_server(model_type):
    cmd = f"python -m qwen_tts.cli.demo {model_type} --ip 0.0.0.0 --port 8000 --no-flash-attn"
    
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process

# Fungsi untuk memeriksa apakah server sudah siap
def is_server_ready(url="http://localhost:8000", timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

# Header aplikasi
st.title("🎙️ Qwen TTS Generator")
st.markdown("---")

# Sidebar untuk konfigurasi
st.sidebar.header("Configuration")

# Pilihan model
model_options = {
    "Built-in Voice": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "Clone Voice from Reference": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "Voice Design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
}

selected_model = st.sidebar.selectbox(
    "Select Model Type:",
    list(model_options.keys())
)

# Instalasi dependencies
if st.sidebar.button("Install Dependencies"):
    if install_dependencies():
        st.sidebar.success("Dependencies installed successfully!")

# Main content
st.subheader(f"Selected Model: {selected_model}")

# Area input teks
text_input = st.text_area(
    "Enter your text:",
    "Hello, welcome to Qwen TTS demo!",
    height=100
)

# Tombol generate
if st.button("Generate Speech", type="primary"):
    if not text_input.strip():
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Processing... Please wait."):
            try:
                # Mulai server
                model_type = model_options[selected_model]
                process = start_tts_server(model_type)
                
                # Tunggu server siap
                if is_server_ready():
                    st.success("Server is ready! You can now use the TTS service.")
                    
                    # Tampilkan informasi server
                    st.info("The TTS server is running locally. You can access it through the command line or integrate it with your application.")
                    
                    # Tampilkan status server
                    st.subheader("Server Status")
                    st.write("✅ Server Running")
                    st.write(f"📦 Model: {selected_model}")
                    st.write("📍 Access: Localhost port 8000")
                    
                    # Petunjuk penggunaan
                    st.subheader("How to Use")
                    st.markdown("""
                    1. The server is running on port 8000
                    2. You can send POST requests to `/tts` endpoint
                    3. Example curl command:
                       ```bash
                       curl -X POST http://localhost:8000/tts \\
                            -H "Content-Type: application/json" \\
                            -d '{"text": "Your text here"}' \\
                            --output output.wav
                       ```
                    """)
                    
                else:
                    st.error("Failed to start server within timeout period.")
                    
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")

# Informasi tambahan
st.markdown("---")
st.subheader("Additional Information")
st.markdown("""
📝 **Notes:**
- This demo uses the Qwen TTS models without requiring API keys
- Make sure to install dependencies first before generating speech
- Different models offer different capabilities:
  - **Built-in Voice**: Uses pre-defined voices
  - **Clone Voice**: Clone voice from reference audio
  - **Voice Design**: Create custom voice characteristics
""")

# Footer
st.markdown("---")
st.caption("Qwen TTS Generator - No API Key Required")
