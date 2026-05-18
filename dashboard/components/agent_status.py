import streamlit as st

class AgentStatus:
    @staticmethod
    def render(mods: dict):
        for name, connected in mods.items():
            status = "🟢" if connected else "🔴"
            st.write(f"{status} {name}")