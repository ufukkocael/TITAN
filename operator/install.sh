# Terminal 1: Operator sunucuyu başlat
cd services/operator
pip install -r requirements.txt
python main.py

# Terminal 2: Dashboard'u başlat
cd services/operator
streamlit run dashboard/app.py --server.port 8501