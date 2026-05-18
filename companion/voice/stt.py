# services/companion/voice/stt.py
import threading
from typing import Optional, Callable

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_AVAILABLE = False

class SpeechToText:
    """Sesi metne çevirir."""
    
    def __init__(self, language: str = "tr-TR"):
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
        self.language = language
        self.is_listening = False
    
    def listen_once(self) -> Optional[str]:
        if not SPEECH_AVAILABLE or not self.recognizer:
            return None
            
        try:
            with sr.Microphone() as source:
                self.is_listening = True
                print("🎤 Dinleniyor...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"👂 Duyulan: {text}")
                return text
        except Exception as e:
            print(f"❌ STT Hatası: {e}")
            return None
        finally:
            self.is_listening = False
    
    def listen_continuous(self, callback: Callable[[str], None]):
        if not SPEECH_AVAILABLE:
            return

        def _listen():
            while True:
                text = self.listen_once()
                if text:
                    callback(text)
        
        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()