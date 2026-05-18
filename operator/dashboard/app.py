# services/operator/dashboard/app.py
import streamlit as st
import pandas as pd
import json
import asyncio
import websockets
import threading
from collections import deque
from datetime import datetime

st.set_page_config(page_title="TITAN Operator", layout="wide")

# Session State
for key, default in {
    'logs': deque(maxlen=200), 'events': deque(maxlen=100),
    'alerts': [], 'nodes': [], 'approval_queue': [],
    'metrics': {"total": 0, "dejavus": 0, "alerts": 0, "status": "Başlatılıyor..."},
    'ws_connected': False, 'ws_started': False
}.items():
    if key not in st.session_state: st.session_state[key] = default

# WebSocket bağlantısı
def ws_worker():
    async def connect():
        try:
            async with websockets.connect("ws://localhost:9001/ws") as ws:
                st.session_state.ws_connected = True
                while True:
                    data = json.loads(await ws.recv())
                    t = data.get("type")
                    if t == "new_log":
                        st.session_state.logs.append(data["data"])
                        st.session_state.metrics["total"] += 1
                    elif t == "alert":
                        st.session_state.alerts.append({**data["data"], "time": datetime.now().isoformat()})
                        st.session_state.metrics["alerts"] = len(st.session_state.alerts)
                    elif t == "dejavu":
                        st.session_state.events.append(f"✨ Dejavu: {data['data']['concept']}")
                        st.session_state.metrics["dejavus"] += 1
                    elif t == "oversoul_insight":
                        d = data["data"]
                        st.session_state.events.append(f"🔮 Oversoul: {d.get('root_cause','?')} (%{d.get('confidence',0)*100:.0f})")
                    elif t == "healer_approval_required":
                        st.session_state.approval_queue.append(data)
                    elif t == "healer_result":
                        d = data["data"]
                        st.session_state.events.append(f"🛠️ Healer: {d.get('status')}")
                    elif t == "system_status":
                        st.session_state.metrics["status"] = data["data"]["message"]
        except Exception as e:
            st.session_state.ws_connected = False
    asyncio.new_event_loop().run_until_complete(connect())

if not st.session_state.ws_started:
    threading.Thread(target=ws_worker, daemon=True).start()
    st.session_state.ws_started = True

# Arayüz
st.title("🛡️ TITAN Operator Mode")
st.caption(f"Bağlantı: {'🟢 Canlı' if st.session_state.ws_connected else '🔴 Kopuk'}")

c1, c2, c3, c4 = st.columns(4)
m = st.session_state.metrics
c1.metric("Loglar", m["total"])
c2.metric("Dejavu", m["dejavus"])
c3.metric("Aktif Uyarı", m["alerts"])
c4.metric("Durum", m["status"])

st.divider()
st.subheader("⚠️ Uyarı Paneli")
if st.session_state.alerts:
    for a in st.session_state.alerts[-5:]:
        st.error(f"🚨 [{a.get('platform','?')}] {a.get('message','')}")
    if st.button("Uyarıları Temizle"):
        st.session_state.alerts.clear()
        st.session_state.metrics["alerts"] = 0
        st.rerun()
else:
    st.success("✅ Aktif uyarı yok")

st.divider()
st.subheader("📜 Son Loglar")
for _, row in pd.DataFrame(list(st.session_state.logs)[-15:]).iterrows():
    sev = row.get('severity', 'INFO')
    color = "red" if sev in ("FATAL","CRITICAL") else ("orange" if sev == "WARN" else "white")
    st.markdown(f"<span style='color:{color}'>[{row.get('platform','?')}] {row.get('message','')[:100]}</span>", unsafe_allow_html=True)

st.divider()
st.subheader("⚡ Olay Akışı")
for e in reversed(list(st.session_state.events)[-10:]):
    st.write(e)

# Healer Onay
if st.session_state.approval_queue:
    st.divider()
    st.subheader("⚠️ Healer Onay Bekliyor")
    app_data = st.session_state.approval_queue[0]
    st.warning(f"Seviye: {app_data.get('level','?')}")
    st.json(app_data.get("recommendation", {}))
    c1, c2 = st.columns(2)
    if c1.button("✅ Onayla"):
        async def send():
            async with websockets.connect("ws://localhost:9001/ws") as ws:
                await ws.send(json.dumps({"type":"healer_approval_response","approval_id":app_data["approval_id"],"accepted":True}))
        asyncio.new_event_loop().run_until_complete(send())
        st.session_state.approval_queue.pop(0)
        st.rerun()
    if c2.button("❌ Reddet"):
        st.session_state.approval_queue.pop(0)
        st.rerun()