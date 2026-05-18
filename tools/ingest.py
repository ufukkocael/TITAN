# titan-core/titan/tools/ingest.py
import os
import re
from typing import List, Dict
from pathlib import Path

class DocumentIngestTool:
    """TITAN'a PDF, Metin ve diğer belgeleri öğreten araç."""
    
    def __init__(self, upload_dir: str = "./imports"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
    def read_text_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except: return ""

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += p + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        if current_chunk: chunks.append(current_chunk.strip())
        return chunks

    async def ingest_directory(self, folder_path: str) -> List[Dict]:
        results = []
        p = Path(folder_path)
        if not p.exists(): return []
        
        # Sadece .txt ve .md dosyalarını tara
        for ext in ["*.txt", "*.md"]:
            for file in p.glob(f"**/{ext}"):
                content = self.read_text_file(str(file))
                if content:
                    chunks = self.chunk_text(content)
                    results.append({
                        "filename": file.name,
                        "chunks": chunks
                    })
        return results
