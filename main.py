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

# KAYDET BUTONU
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

# NOTLARI GÖRÜNTÜLE BUTONU
# Notları listeleyen fonksiyon (detay görüntüleme dahil)
def show_notes():
    list_window = tk.Toplevel(root)                          # Yeni pencere (popup) oluştur
    list_window.title("📋 Kayıtlı Notlar")                    # Yeni pencere başlığı

    scrollbar = tk.Scrollbar(list_window)                    # Kaydırma çubuğu oluştur
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)                 # Sağ tarafa yerleştir

    listbox = tk.Listbox(list_window, width=80, height=15, yscrollcommand=scrollbar.set)  # Notları gösterecek kutu
    listbox.pack(padx=10, pady=10)                           # Kutuyu yerleştir

    scrollbar.config(command=listbox.yview)                  # Scrollbar ile listbox bağlantısı

    conn = sqlite3.connect("notlar.db")                      # Veritabanına bağlan
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")  # Tüm notları çek
    notes = cursor.fetchall()
    conn.close()

    note_ids = []                                            # Seçilen notların ID'sini takip etmek için liste

    for note in notes:                                       # Her not için satır ekle
        note_id, title, content, created_at = note
        listbox.insert(tk.END, f"🕒 {created_at} | {title}")  # Listbox'a notları ekle
        note_ids.append(note_id)                             # ID'leri sırayla listeye kaydet

    # Çift tıklanınca detaylı görüntüleme
    def on_note_select(event):
        selection = listbox.curselection()                   # Seçilen satırı bul
        if selection:
            index = selection[0]                             # Seçilen satırın index'ini al
            selected_id = note_ids[index]                    # O satırın not ID’sini getir

            conn = sqlite3.connect("notlar.db")              # Veritabanına tekrar bağlan
            cursor = conn.cursor()
            cursor.execute("SELECT title, content, created_at FROM notes WHERE id = ?", (selected_id,))
            note = cursor.fetchone()
            conn.close()

            # Yeni pencere aç → içeriği göster
            detail_window = tk.Toplevel(list_window)
            detail_window.title("📝 Not Detayı")

            title_label = tk.Label(detail_window, text=f"Başlık: {note[0]}", font=("Arial", 12, "bold"))
            title_label.pack(pady=5)

            date_label = tk.Label(detail_window, text=f"Tarih: {note[2]}", font=("Arial", 10))
            date_label.pack(pady=5)

            content_text = tk.Text(detail_window, wrap=tk.WORD, width=60, height=10)
            content_text.insert(tk.END, note[1])             # İçeriği metin kutusuna ekle
            content_text.config(state="disabled")            # Okunabilir ama düzenlenemez yap
            content_text.pack(padx=10, pady=10)

    listbox.bind("<Double-1>", on_note_select)               # Çift tıklama olayını bağla


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
tk.Button(root, text="Notları Görüntüle", command=show_notes).pack(pady=5)  # Notları listeleme butonu

root.mainloop()  # Arayüzü çalıştır
