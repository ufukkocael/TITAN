import streamlit as st
import asyncio
import websockets
import json

class ApprovalModal:
    @staticmethod
    def render(approval_data: dict):
        st.warning(f"⚠️ Healer Onayı Gerekiyor - Seviye: {approval_data.get('level','?')}")
        st.json(approval_data.get("recommendation", {}))
        c1, c2 = st.columns(2)
        if c1.button("✅ Onayla"):
            async def send():
                async with websockets.connect("ws://localhost:9000/ws/gateway") as ws:
                    await ws.send(json.dumps({"type":"healer_approval_response","approval_id":approval_data["approval_id"],"accepted":True}))
            asyncio.new_event_loop().run_until_complete(send())
            return True
        if c2.button("❌ Reddet"):
            return False
        return None