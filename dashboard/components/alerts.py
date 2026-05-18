import streamlit as st

class AlertsPanel:
    @staticmethod
    def render(alerts: list):
        if alerts:
            for alert in alerts[-5:]:
                st.error(f"🚨 {alert.get('platform','?')}: {alert.get('message','')}")
        else:
            st.success("✅ Aktif uyarı yok")