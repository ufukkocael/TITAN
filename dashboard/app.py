import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import asyncio
import websockets
import threading
import time
import requests
from collections import deque
from datetime import datetime

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost:9000"
COMPANION_URL = "http://localhost:9004/api/chat"

st.set_page_config(
    page_title="TITAN V4 | Command Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME & STYLING ---
aesthetic = st.session_state.get("aesthetic_params", {"primary_color": "#00f2ff", "pulse_speed": 1.0})

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'JetBrains+Mono', monospace;
    }}
    
    .main {{
        background-color: #05070a;
    }}
    
    /* Neon glow metrics */
    div[data-testid="stMetricValue"] {{
        color: {aesthetic['primary_color']};
        text-shadow: 0 0 10px {aesthetic['primary_color']}55;
    }}
    
    .chat-bubble {{
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #1e293b;
    }}
    
    .user-bubble {{
        background: #1e293b;
        color: #f8fafc;
        border-left: 4px solid #3b82f6;
    }}
    
    .titan-bubble {{
        background: #0f172a;
        color: {aesthetic['primary_color']};
        border-left: 4px solid {aesthetic['primary_color']};
        box-shadow: inset 0 0 15px {aesthetic['primary_color']}11;
    }}

    /* Thinking animation */
    .loader {{
        border: 4px solid #1a1c24;
        border-top: 4px solid {aesthetic['primary_color']};
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin {2.0 / aesthetic['pulse_speed']}s linear infinite;
    }}
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
for key, default in {
    'chat_history': deque(maxlen=20),
    'logs': deque(maxlen=50),
    'metrics_history': {'time': deque(maxlen=30), 'cpu': deque(maxlen=30), 'mem': deque(maxlen=30)},
    'anxiety_score': 0.0,
    'dream_insights': [],
    'ws_connected': False,
    'thinking': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- WEBSOCKET WORKER ---
def ws_worker():
    async def listen():
        uri = "ws://localhost:9000/ws/gateway"
        while True:
            try:
                async with websockets.connect(uri) as ws:
                    st.session_state.ws_connected = True
                    # Initial subscription
                    await ws.send(json.dumps({"service": "broadcast", "message": {"type": "init"}}))
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        m_type = data.get("type")
                        
                        if m_type == "metrics_update":
                            st.session_state.metrics_history['time'].append(datetime.now().strftime("%H:%M:%S"))
                            st.session_state.metrics_history['cpu'].append(data["data"].get("cpu", 0))
                            st.session_state.metrics_history['mem'].append(data["data"].get("mem", 0))
                            st.session_state.aesthetic_params = data["data"].get("aesthetic", {})
                        elif m_type == "dream_insight":
                            st.session_state.dream_insights.append(data["data"])
                        elif m_type == "new_log":
                            st.session_state.logs.append(data["data"])
            except:
                st.session_state.ws_connected = False
                time.sleep(5)
    
    asyncio.new_event_loop().run_until_complete(listen())

if 'thread_started' not in st.session_state:
    threading.Thread(target=ws_worker, daemon=True).start()
    st.session_state.thread_started = True

# --- HELPER FUNCTIONS ---
def send_message(text):
    st.session_state.thinking = True
    st.session_state.chat_history.append({"role": "user", "content": text})
    try:
        response = requests.post(COMPANION_URL, json={"message": text}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.chat_history.append({"role": "titan", "content": data.get("response")})
        else:
            st.error("Companion connection failed.")
    except Exception as e:
        st.error(f"Error: {e}")
    st.session_state.thinking = False

# --- SIDEBAR (SYSTEM CONTROLS) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/UKMAK/titan-assets/main/logo_neon.png", width=200) # Optional logo placeholder
    st.title("🛡️ TITAN CORE")
    
    status_color = "green" if st.session_state.ws_connected else "red"
    st.markdown(f"Status: :{status_color}[{'ONLINE' if st.session_state.ws_connected else 'OFFLINE'}]")
    
    st.divider()
    st.subheader("Bilişsel Kontroller")
    st.toggle("REM Phase (Dreaming)", value=False, help="Sistemi yapay rüya moduna sokar.")
    st.toggle("Quantum Superposition", value=True, help="Olasılıksal düşünme motorunu aktif eder.")
    
    st.divider()
    st.subheader("Quick Actions")
    if st.button("🔍 Perform System Scan"):
        st.toast("Scanning all modules for anomalies...")
    if st.button("🧹 Flush Volatile Memory"):
        st.toast("Working memory cleared.")
        
    st.divider()
    st.caption("TITAN V4.0.2-Stable")

# --- MAIN INTERFACE ---
# Tab Navigation
tab_chat, tab_neural, tab_ops = st.tabs(["💬 INTERACTIVE AI", "🧠 NEURAL TESSERACT", "⚙️ SYSTEM OPERATIONS"])

with tab_chat:
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.subheader("Neural Interface")
        
        # Chat Display
        chat_container = st.container(height=500)
        for chat in st.session_state.chat_history:
            role_class = "user-bubble" if chat["role"] == "user" else "titan-bubble"
            chat_container.markdown(f"""
            <div class='chat-bubble {role_class}'>
                <b>{'YOU' if chat['role']=='user' else 'TITAN'}</b><br>{chat['content']}
            </div>
            """, unsafe_allow_html=True)
            
        if st.session_state.thinking:
            st.markdown("<div class='loader'></div>", unsafe_allow_html=True)
            
        # Chat Input
        if prompt := st.chat_input("Command or message..."):
            send_message(prompt)
            st.rerun()

    with col_c2:
        st.subheader("Real-time Cognition")
        st.metric("Existential Anxiety", f"{st.session_state.anxiety_score:.2f}")
        st.metric("Subjective Dilatation", "x1.42")
        
        st.divider()
        st.subheader("Recent Insights")
        if st.session_state.dream_insights:
            for insight in reversed(st.session_state.dream_insights[-5:]):
                st.info(f"✨ {insight}")
        else:
            st.write("Collecting latent data...")

with tab_neural:
    st.subheader("4D Concept Mapping")
    # Interactive 3D Plot
    df_nodes = pd.DataFrame({
        'x': [10, 20, 15, 40, 50, 30, 25, 35],
        'y': [20, 10, 25, 30, 10, 40, 35, 15],
        'z': [30, 40, 35, 20, 50, 10, 15, 25],
        'Concept': ['Self', 'Security', 'User', 'Ethics', 'Logic', 'Code', 'Risk', 'Harmony'],
        'Energy': [0.9, 0.4, 0.7, 0.8, 0.9, 0.5, 0.3, 0.6]
    })
    
    fig = px.scatter_3d(df_nodes, x='x', y='y', z='z', text='Concept', 
                         color='Energy', size='Energy', size_max=20,
                         color_continuous_scale='Portland',
                         template="plotly_dark")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Active Archetypes")
    st.multiselect("Bilinçaltı Odakları", ["Protector", "Optimizer", "Creator"], default=["Protector", "Creator"])

with tab_ops:
    col_o1, col_o2 = st.columns(2)
    
    with col_o1:
        st.subheader("Hardware Telemetry")
        if len(st.session_state.metrics_history['time']) > 0:
            df_metrics = pd.DataFrame({
                'Time': list(st.session_state.metrics_history['time']),
                'CPU %': list(st.session_state.metrics_history['cpu']),
                'Memory %': list(st.session_state.metrics_history['mem'])
            })
            # Multi-line chart
            st.line_chart(df_metrics.set_index('Time'))
    
    with col_o2:
        st.subheader("Active Goal Engine")
        st.progress(85, text="Goal: System Stability (85%)")
        st.progress(42, text="Goal: Evolutionary Learning (42%)")
        st.progress(12, text="Goal: Hypothesis Testing (12%)")

    st.divider()
    st.subheader("Distributed Log Stream")
    for log in reversed(list(st.session_state.logs)):
        sev = log.get('severity', 'INFO')
        color = "red" if sev in ("FATAL", "CRITICAL") else ("orange" if sev == "WARN" else "gray")
        st.markdown(f":{color}[[{log.get('service', 'SYS')}] {log.get('message')}]")

# Footer
st.divider()
bottom_col1, bottom_col2 = st.columns([3, 1])
bottom_col1.markdown("© 2026 **U.KOCAEL** | TITAN Synthetic Intelligence Architecture")
if bottom_col2.button("🚨 EMERGENCY SHUTDOWN"):
    st.warning("Initiating safety protocols...")
