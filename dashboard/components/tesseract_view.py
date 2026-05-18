import streamlit as st
import plotly.express as px
import pandas as pd

class TesseractView:
    @staticmethod
    def render(nodes: list):
        if not nodes:
            st.info("Henüz node verisi yok.")
            return
        df = pd.DataFrame(nodes[-100:])
        if not df.empty and 'x' in df.columns:
            fig = px.scatter_3d(df, x='x', y='y', z='z', color='w', size='w', color_continuous_scale='viridis', hover_name='concept')
            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), height=400)
            st.plotly_chart(fig, use_container_width=True)