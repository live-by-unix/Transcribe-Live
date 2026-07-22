import streamlit as st
import tempfile
import os
import zipfile
from datetime import datetime
from TTS.api import TTS

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="TranscribeLive", layout="centered")

st.title("🎙️ TranscribeLive")

# Theme toggle
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

st.button("Toggle Theme", on_click=toggle_theme)
st.write(f"Current theme: {st.session_state.theme}")

# Record or upload audio
st.subheader("Upload or Record Voice Sample")
voice_sample = st.file_uploader("Upload a 20s clip", type=["wav","m4a"])

# Transcript input
transcript = st.text_area("Type your transcript here")

# Simulate button
if st.button("Simulate"):
    if voice_sample and transcript:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(voice_sample.read())
            sample_path = tmp.name

        # Load pretrained voice cloning model
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

        # Generate cloned audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_{timestamp}.wav"
        tts.tts_to_file(text=transcript, speaker_wav=sample_path, file_path=output_path)

        # Save to history
        st.session_state.history.append({
            "transcript": transcript,
            "audio_path": output_path,
            "timestamp": timestamp
        })

        # Playback
        st.success("Simulation complete!")
        st.audio(output_path)

        # Export bundle (transcript + audio)
        bundle_path = f"bundle_{timestamp}.zip"
        with zipfile.ZipFile(bundle_path, "w") as zipf:
            zipf.write(output_path)
            txt_path = f"transcript_{timestamp}.txt"
            with open(txt_path, "w") as f:
                f.write(transcript)
            zipf.write(txt_path)
        st.download_button("Download Bundle", data=open(bundle_path, "rb"), file_name=bundle_path)

# History panel
st.subheader("History")
for item in st.session_state.history[::-1]:
    st.markdown(f"**{item['timestamp']}** — Transcript:")
    st.write(item["transcript"])
    st.audio(item["audio_path"])
