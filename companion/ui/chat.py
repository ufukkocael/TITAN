# services/companion/ui/chat.py
import streamlit as st
import requests
import json
from datetime import datetime

API_URL = "http://localhost:9004/api/chat"

st.set_page_config(page_title="TITAN Companion", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.chat-container { max-width: 700px; margin: auto; }
.user-msg { background: #1a3a5c; border-radius: 15px 15px 0 15px; padding: 12px; margin: 8px 0; text-align: right; }
.titan-msg { background: #2a1a3c; border-radius: 15px 15px 15px 0; padding: 12px; margin: 8px 0; text-align: left; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 TITAN Companion")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "titan", "content": "Merhaba! Ben TITAN. Size nasıl yardımcı olabilirim?", "time": datetime.now().isoformat()}
    ]

# Sohbet geçmişi
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="titan-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

# Girdi alanı
user_input = st.chat_input("Mesajınızı yazın...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "time": datetime.now().isoformat()})
    
    try:
        response = requests.post(API_URL, json={"message": user_input}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            titan_response = data.get("response", "Üzgünüm, şu anda cevap veremiyorum.")
        else:
            titan_response = "Bağlantı hatası oluştu."
    except Exception:
        titan_response = "Sunucuya ulaşılamıyor."
    
    st.session_state.messages.append({"role": "titan", "content": titan_response, "time": datetime.now().isoformat()})
    st.rerun()

# İlişki durumu
with st.sidebar:
    st.subheader("📊 İlişki Durumu")
    try:
        status = requests.get("http://localhost:9004/api/relationship", timeout=5).json()
        st.metric("Seviye", status.get("level", "?"))
        st.metric("Konuşma Sayısı", status.get("conversations", 0))
        st.metric("Güven Skoru", f"{status.get('trust_score', 0):.2f}")
    except:
        st.warning("Bağlantı bekleniyor...")