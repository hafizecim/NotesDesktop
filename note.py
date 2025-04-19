"""
🧱 note.py - Not Sınıfı

Bu sınıf, bir notun temel özelliklerini temsil eder:
- Başlık
- İçerik
- Oluşturulma tarihi

Hazırlayan: Hafize Şenyıl
"""

class Note:
    def __init__(self, title, content, created_at=None):
        self.title = title            # Notun başlığı
        self.content = content        # Notun içeriği
        self.created_at = created_at  # Notun oluşturulma zamanı (varsayılan: None)
