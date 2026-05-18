import streamlit as st
import pandas as pd

class LogStream:
    @staticmethod
    def render(logs: list):
        df = pd.DataFrame(logs[-20:])
        for _, row in df.iterrows():
            sev = row.get('severity', 'INFO')
            color = "red" if sev in ("FATAL","CRITICAL") else ("orange" if sev=="WARN" else "white")
            st.markdown(f"<span style='color:{color}'>[{row.get('platform','?')}] {row.get('message','')[:100]}</span>", unsafe_allow_html=True)