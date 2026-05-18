# services/companion/voice/tts.py
import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    TTS_AVAILABLE = False

class TextToSpeech:
    """Metni sese çevirir."""
    
    def __init__(self, speed: int = 150):
        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', speed)
            except Exception:
                self.engine = None
        self.speaking = False
    
    def speak(self, text: str):
        if not self.engine:
            return
            
        def _speak():
            self.speaking = True
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
            self.speaking = False
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
    
    def is_speaking(self) -> bool:
        return self.speaking