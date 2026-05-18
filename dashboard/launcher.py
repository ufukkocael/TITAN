# dashboard/launcher.py
import webview
import os
import sys
import threading
import time
from pathlib import Path

def start_window():
    """HTML dosyasını masaüstü penceresinde açar."""
    html_path = Path(__file__).parent / "index.html"
    
    # Modern tarayıcı çekirdeğini (Edge/WebView2) zorla
    window = webview.create_window(
        'TITAN V4 | Full Stack Neural Interface',
        str(html_path.resolve()),
        width=1400,
        height=900,
        background_color='#03030a'
    )
    
    # Windows'ta Edge Chromium (WebView2) motorunu kullanmasını sağla
    webview.start(gui='edgechromium', debug=True)

if __name__ == "__main__":
    print("🚀 TITAN Masaüstü Arayüzü başlatılıyor...")
    start_window()
