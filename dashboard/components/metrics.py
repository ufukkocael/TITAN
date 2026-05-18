import streamlit as st

class MetricsCards:
    @staticmethod
    def render(metrics: dict):
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            col.metric(label, value)