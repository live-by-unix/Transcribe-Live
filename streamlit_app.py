import streamlit as st
import tempfile
import os
import zipfile
from datetime import datetime
from TTS.api import TTS
import base64

st.set_page_config(page_title="TranscribeLive", layout="centered")
st.title("🎙️ TranscribeLive")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Upload or Record Voice Sample")

# Upload option
voice_sample = st.file_uploader("Upload a 20s clip", type=["wav","m4a"])

# Record option via HTML/JS
recorder_html = """
<script>
let chunks = [];
let recorder;
function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => chunks.push(e.data);
    recorder.onstop = e => {
      let blob = new Blob(chunks, { type: 'audio/wav' });
      let reader = new FileReader();
      reader.onload = () => {
        const base64data = reader.result.split(',')[1];
        const pyMsg = { "audio": base64data };
        window.parent.postMessage(pyMsg, "*");
      };
      reader.readAsDataURL(blob);
      chunks = [];
    };
    recorder.start();
    setTimeout(() => recorder.stop(), 20000); // auto-stop after 20s
  });
}
</script>
<button onclick="startRecording()">🎤 Record 20s</button>
"""
st.components.v1.html(recorder_html, height=100)

# Transcript input
transcript = st.text_area("Type your transcript here")

# Handle recorded audio from browser
recorded_audio = None
if "audio" in st.session_state:
    recorded_audio = base64.b64decode(st.session_state.audio)

# Simulate button
if st.button("Simulate"):
    if (voice_sample or recorded_audio) and transcript:
        if voice_sample:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(voice_sample.read())
                sample_path = tmp.name
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(recorded_audio)
                sample_path = tmp.name

        # Voice cloning
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_{timestamp}.wav"
        tts.tts_to_file(text=transcript, speaker_wav=sample_path, file_path=output_path)

        # Save to history
        st.session_state.history.append({
            "transcript": transcript,
            "audio_path": output_path,
            "timestamp": timestamp
        })

        st.success("Simulation complete!")
        st.audio(output_path)

        # Export bundle
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
