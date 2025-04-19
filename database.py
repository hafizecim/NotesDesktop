"""
📂 database.py - Veritabanı İşlemleri

Bu modül, SQLite kullanarak "notes" tablosunu oluşturur.
Eğer tablo daha önce oluşturulmuşsa tekrar oluşturmaz (CREATE IF NOT EXISTS).

Tablo yapısı:
- id (INTEGER, otomatik artan)
- title (TEXT)
- content (TEXT)
- created_at (TEXT - zaman damgası)

Hazırlayan: Hafize Şenyıl
"""

import sqlite3  # SQLite veritabanı kütüphanesi

def create_db():
    connection = sqlite3.connect("notlar.db")  # Veritabanı bağlantısı kur
    cursor = connection.cursor()               # SQL komutları için imleç oluştur

    # Notlar tablosunu oluştur (yoksa)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT
    )
    """)

    connection.commit()   # Değişiklikleri kaydet
    connection.close()    # Bağlantıyı kapat
