import streamlit as st
import requests
import time
import os
import json

# === CONFIGURATION ===
_auth_token = st.secrets["HF_API_TOKEN"]  # Securely pulled from secrets
ASSISTANT_ID = "68610acc741e47a5740c9c7b"
HF_API_URL = "https://api-inference.huggingface.co/chat/completions"
XP_SAVE_FILE = "xp_state.json"
JOURNAL_SAVE_FILE = "journal_log.txt"

# === LOAD XP FROM FILE ===
def load_xp():
    if os.path.exists(XP_SAVE_FILE):
        with open(XP_SAVE_FILE, "r") as f:
            data = json.load(f)
            return data.get("xp", 0)
    return 0

# === SAVE XP TO FILE ===
def save_xp(xp):
    with open(XP_SAVE_FILE, "w") as f:
        json.dump({"xp": xp}, f)

# === INITIAL STATE ===
if "xp" not in st.session_state:
    st.session_state.xp = load_xp()
if "bruce_journaled" not in st.session_state:
    st.session_state.bruce_journaled = False
if "umbra_journaled" not in st.session_state:
    st.session_state.umbra_journaled = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "stopwatch_running" not in st.session_state:
    st.session_state.stopwatch_running = False

# === JOURNAL SAVE FUNCTION ===
def save_journal_entry(name, content):
    with open(JOURNAL_SAVE_FILE, "a") as f:
        f.write(f"\n{name} Journal - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(content + "\n" + ("-" * 40) + "\n")

# === FUNCTIONS ===
def get_alfred_response(user_message):
    headers = {
        "Authorization": f"Bearer {_auth_token}"
    }
    data = {
        "messages": [{"role": "user", "content": user_message}],
        "assistant_id": ASSISTANT_ID
    }
    response = requests.post(HF_API_URL, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# === BATCAVE UI ===
st.set_page_config(page_title="Batcave XP Console", layout="centered")
st.markdown("""
    <h1 style='color:#00ffcc;'>🦇 Batcave XP System</h1>
    <audio autoplay hidden>
      <source src="https://firebasestorage.googleapis.com/v0/b/stuff-storage-999.appspot.com/o/batman2022.mp3?alt=media" type="audio/mp3">
    </audio>
""", unsafe_allow_html=True)

# === JOURNALING SECTION (Bruce) ===
st.markdown("""
### Bruce⚡ Journal
> **This is the version of you that is razor-sharp, relentless, and committed to excellence.**
> 
> Inspired by Carl Jung’s shadow self, Bruce is not soft. He is the ideal. Until you write like him, you're not ready to face the mission.
""")

bruce_entry = st.text_area("Journal as Bruce before you begin:", placeholder="What does the disciplined you look like today?")
if bruce_entry:
    st.session_state.bruce_journaled = True
    save_journal_entry("Bruce", bruce_entry)
    st.success("Bruce mode activated. You're cleared to proceed.")

# === TASK SECTION ===
if st.session_state.bruce_journaled:
    task = st.text_input("Describe your task")
    proof = st.text_area("Paste your proof or summary")
    file = st.file_uploader("Upload your proof file")

    user_reward_type = st.radio("Choose your reward type:", ["Embed video/movie link", "Custom reward text"])

    if user_reward_type == "Embed video/movie link":
        reward_link = st.text_input("Paste your YouTube or video link here")
    else:
        reward_text = st.text_input("Describe your custom reward (e.g., Read comic, Take nap, etc.)")

    if st.button("🕵️ Ask Alfred to Verify"):
        with st.spinner("Alfred is reviewing your proof..."):
            query = f"Master Wayne has completed the task: {task}. Proof: {proof if proof else '[file uploaded]'} — Is this valid?"
            alfred_reply = get_alfred_response(query)
            st.success(f"🧠 Alfred: {alfred_reply}")
            if any(x in alfred_reply.lower() for x in ["approved", "valid", "verified", "meets"]):
                st.session_state.xp += 20
                save_xp(st.session_state.xp)
                st.balloons()
                st.success(f"+20 XP gained. Total XP: {st.session_state.xp}")
            else:
                st.warning("No XP awarded. Alfred requires better proof.")

    st.markdown(f"### 🧬 Current XP: {st.session_state.xp} / 100")

    # === STOPWATCH & TIMER ===
    st.markdown("---")
    st.markdown("## ⏱ Time Tools")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Stopwatch"):
            st.session_state.start_time = time.time()
            st.session_state.stopwatch_running = True
        if st.button("⏹ Stop Stopwatch"):
            if st.session_state.start_time:
                elapsed = time.time() - st.session_state.start_time
                st.success(f"⏱ Elapsed Time: {int(elapsed // 60)} min {int(elapsed % 60)} sec")
                st.session_state.stopwatch_running = False

    with col2:
        timer_min = st.number_input("Set countdown timer (minutes)", min_value=1, value=25)
        if st.button("⏳ Start Timer"):
            st.info(f"Timer started for {timer_min} minutes.")
            time.sleep(timer_min * 60)
            st.success("⏰ Time’s up, Master Wayne!")

    # === UMBRA JOURNALING ===
    if st.session_state.xp >= 100:
        st.markdown("""
        ### Joker 🃏 Final Journal
        > The Joker is the unfiltered chaos within — your grinning shadow, the clown prince of your repressed madness, the voice that laughs when the world burns. 
        > 
        > Only when you meet him, you may rest. Complete this to unlock your full reward.
        """)
        joker_entry = st.text_area("Journal as the Joker:", placeholder="Speak madness. Write what you refuse to admit.")
        if joker_entry:
            st.session_state.joker_journaled = True
            save_journal_entry("Joker", joker_entry)
            st.success("The Joker has spoken. Chaos complete. Reward unlocked.")

    # === UNLOCK FINAL REWARD ===
    if st.session_state.xp >= 100 and st.session_state.joker_journaled:
        st.success("🎬 Full movie unlocked.")
        if user_reward_type == "Embed video/movie link" and reward_link:
            st.video(reward_link)
        elif user_reward_type == "Custom reward text" and reward_text:
            st.info(f"Reward: {reward_text}")
    elif st.session_state.xp >= 60:
        st.info("🟦 30-minute video unlocked.")
    elif st.session_state.xp >= 40:
        st.info("🟩 20-minute video unlocked.")
    elif st.session_state.xp >= 20:
        st.info("🟨 10-minute video unlocked.")
    else:
        st.error("🔒 Keep grinding, Master Wayne.")

# === STYLING ===
st.markdown("""
    <style>
    body {
        background-color: #0a0a0a;
        color: #00ffcc;
        font-family: 'Courier New', monospace;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: #00ffcc;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)
