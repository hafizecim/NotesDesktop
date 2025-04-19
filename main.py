"""
📝 Not Defteri Uygulaması (Masaüstü - Tkinter ile)

Bu uygulama, kullanıcıdan bir başlık ve içerik alarak notlarını kaydetmesini sağlar.
Notlar, SQLite veritabanında saklanır. Arayüz olarak Tkinter kullanılmıştır.

Özellikler:
- Kullanıcıdan başlık ve içerik alınır
- Veritabanına (notlar.db) kayıt yapılır
- Boş başlık kontrolü vardır
- Başarılı işlem sonrası kullanıcı bilgilendirilir

Hazırlayan: Hafize Şenyıl
"""

import tkinter as tk                      # Arayüz oluşturmak için Tkinter modülü
from tkinter import messagebox           # Uyarı ve bilgi kutuları için
from datetime import datetime            # Zaman bilgisi eklemek için
import sqlite3                           # SQLite veritabanı işlemleri için

from database import create_db           # Veritabanı oluşturma fonksiyonunu içe aktar

# Veritabanını oluştur (eğer yoksa)
create_db()

# Not kaydeden fonksiyon
def save_note():
    title = title_entry.get()                                      # Başlık girişinden veriyi al
    content = content_text.get("1.0", tk.END)                      # İçerik metnini al (1. satırdan itibaren, END'e kadar)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")      # Şu anki tarihi formatlı olarak al

    if not title.strip():                                          # Başlık boş mu kontrol et
        messagebox.showwarning("Uyarı", "Başlık boş olamaz.")     # Boşsa uyarı ver
        return

    # Veritabanına bağlan
    conn = sqlite3.connect("notlar.db")
    cursor = conn.cursor()

    # Veriyi veritabanına ekle
    cursor.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
                   (title, content, created_at))
    conn.commit()   # Değişiklikleri kaydet
    conn.close()    # Bağlantıyı kapat

    messagebox.showinfo("Başarılı", "Not kaydedildi!")             # Başarılı mesajı
    title_entry.delete(0, tk.END)                                  # Başlığı temizle
    content_text.delete("1.0", tk.END)                             # İçeriği temizle

# Tkinter ile arayüz tasarımı
root = tk.Tk()                             # Ana pencereyi oluştur
root.title("📝 Not Defteri Uygulaması")    # Pencere başlığı

tk.Label(root, text="Başlık:").pack()     # Başlık etiketi
title_entry = tk.Entry(root, width=50)    # Başlık girişi
title_entry.pack()

tk.Label(root, text="İçerik:").pack()     # İçerik etiketi
content_text = tk.Text(root, height=10, width=50)  # İçerik kutusu
content_text.pack()

tk.Button(root, text="Kaydet", command=save_note).pack(pady=10)   # Kaydet butonu

root.mainloop()  # Arayüzü çalıştır
