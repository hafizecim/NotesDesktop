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
    list_window.title("📋 Kayıtlı Notlar")
    list_window.configure(bg="#fff8f0")  # 🔥 Sıcak pastel arka plan

    # 🔍 ARAMA KUTUSU VE BUTONU EKLENİYOR
    search_frame = tk.Frame(list_window, bg="#fff8f0")              # Arama kutusu ve buton için yatay bir çerçeve oluştur
    search_frame.pack(pady=5)                         # Çerçeveyi pencereye yerleştir (üstte olacak)

    # Arama kutusu başlığı (etiket)
    tk.Label(search_frame, text="🔎 Başlıkta Ara:", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

    search_entry = tk.Entry(search_frame, width=30, bg="white", fg="#3e3e3e", font=("Segoe UI", 10))   # Kullanıcının arama yapacağı giriş kutusu
    search_entry.pack(side=tk.LEFT, padx=5)           # Kutuyu çerçeveye sola hizalı ekle

    # 🔄 ARAMA İŞLEVİNİ YAPAN FONKSİYON
    def search_notes():
        keyword = search_entry.get().lower()          # Kullanıcının yazdığı metni al, küçük harfe çevir
        listbox.delete(0, tk.END)                     # Mevcut liste temizleniyor
        note_ids.clear()                              # Daha önceki ID listesi de temizleniyor

        # Notlar listesinde arama yap
        for i, note in enumerate(notes):              # notes: veritabanından çekilen tüm notlar
            note_id, title, content, created_at = note
            if keyword in title.lower():              # Başlık içinde aranan kelime var mı kontrol et
                listbox.insert(tk.END, f"🕒 {created_at} | {title}")  # Uyan başlığı listeye ekle
                note_ids.append(note_id)              # Uyumlu notun ID’sini de notlar listesine ekle


    # 📤 NOTLARI .TXT DOSYASINA DIŞA AKTARAN FONKSİYON
    def export_notes_to_txt():
        # 💾 Veritabanına bağlanıyoruz
        conn = sqlite3.connect("notlar.db")
        cursor = conn.cursor()

        # 📦 Tüm notları tarih sırasına göre çekiyoruz
        cursor.execute("SELECT title, content, created_at FROM notes ORDER BY created_at DESC")
        all_notes = cursor.fetchall()  # Notları liste olarak alıyoruz
        conn.close()  # 🔐 Bağlantıyı kapatıyoruz

        # ❗ Hiç not yoksa kullanıcıya bilgi ver
        if not all_notes:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak not bulunamadı.")
            return

        # 📁 TXT dosyasına yazma işlemi başlıyor
        with open("notlar_export.txt", "w", encoding="utf-8") as file:
            for note in all_notes:
                title, content, created_at = note

                # 📄 Notları güzelce formatlayarak dosyaya yazıyoruz
                file.write(f"🕒 {created_at}\n")        # Notun oluşturulma tarihi
                file.write(f"Başlık: {title}\n")       # Notun başlığı
                file.write("İçerik:\n")                # Sabit içerik başlığı
                file.write(content + "\n")             # Notun içeriği
                file.write("-" * 50 + "\n")            # Aralara çizgi çekiyoruz (ayraç)

        # ✅ Kullanıcıya başarı mesajı göster
        messagebox.showinfo("Başarılı", "Notlar 'notlar_export.txt' dosyasına başarıyla aktarıldı.")

        # 📤 NOTLARI .CSV DOSYASINA DIŞA AKTARAN FONKSİYON

    def export_notes_to_csv():
        import csv  # 📦 csv modülünü kullanıyoruz

        # 💾 Veritabanına bağlan
        conn = sqlite3.connect("notlar.db")
        cursor = conn.cursor()

        # 📦 Tüm notları çek (tarih sırasıyla)
        cursor.execute("SELECT title, content, created_at FROM notes ORDER BY created_at DESC")
        all_notes = cursor.fetchall()
        conn.close()

        # ❗ Hiç not yoksa kullanıcıya bilgi ver
        if not all_notes:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak not bulunamadı.")
            return

        # 📁 CSV dosyasını yazmak için açıyoruz
        with open("notlar_export.csv", "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            # 🧱 Başlık satırını yaz
            writer.writerow(["Tarih", "Başlık", "İçerik"])

            # 🧾 Notları satır satır yaz
            for note in all_notes:
                title, content, created_at = note
                writer.writerow([created_at, title, content])

        # ✅ Kullanıcıya bilgilendirme
        messagebox.showinfo("Başarılı", "Notlar 'notlar_export.csv' dosyasına başarıyla aktarıldı.")


    # 🔍 Ara butonu, tıklanınca arama fonksiyonunu çalıştırır
    tk.Button(search_frame, text="Ara", command=search_notes,
              bg="#6b4c9a", fg="white", font=("Segoe UI", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)


    list_window.title("📋 Kayıtlı Notlar")                    # Yeni pencere başlığı

    scrollbar = tk.Scrollbar(list_window)                    # Kaydırma çubuğu oluştur
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)                 # Sağ tarafa yerleştir

    # Notları gösterecek kutu
    listbox = tk.Listbox(list_window, width=80, height=15,
                         yscrollcommand=scrollbar.set,
                         bg="white", fg="#3e3e3e", font=("Segoe UI", 10),
                         selectbackground="#ffe066", selectforeground="#000")
    listbox.pack(padx=10, pady=10)                           # Kutuyu yerleştir

    scrollbar.config(command=listbox.yview)                  # Scrollbar ile listbox bağlantısı

    conn = sqlite3.connect("notlar.db")                      # Veritabanına bağlan
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")  # Tüm notları çek
    notes = cursor.fetchall()
    conn.close()

    note_ids = []                                            # Seçilen notların ID'sini takip etmek için liste

    # Listbox'a notları yaz
    for note in notes:                                       # Her not için satır ekle
        note_id, title, content, created_at = note
        listbox.insert(tk.END, f"🕒 {created_at} | {title}")  # Listbox'a notları ekle
        note_ids.append(note_id)                             # ID'leri sırayla listeye kaydet

    # Notu silen fonksiyon
    def delete_selected_note():
        selection = listbox.curselection()  # Seçilen satır
        if selection:
            index = selection[0]
            selected_id = note_ids[index]   # O satırın ID’si

            confirm = messagebox.askyesno("Onay", "Bu notu silmek istediğine emin misin?")
            if confirm:
                # Veritabanından sil
                conn = sqlite3.connect("notlar.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes WHERE id = ?", (selected_id,))
                conn.commit()
                conn.close()

                # Listbox’tan kaldır
                listbox.delete(index)
                note_ids.pop(index)  # ID listemizi de güncelle

                messagebox.showinfo("Silindi", "Not başarıyla silindi.")
        else:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir not seç.")

    # Seçilen notu güncelleme fonksiyonu
    def update_selected_note():
        selection = listbox.curselection()  # Seçilen satır kontrolü
        if selection:
            index = selection[0]
            selected_id = note_ids[index]   # Seçilen notun ID'si

            # Notun mevcut verisini veritabanından al
            conn = sqlite3.connect("notlar.db")
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM notes WHERE id = ?", (selected_id,))
            note = cursor.fetchone()
            conn.close()

            # Güncelleme penceresi aç
            update_window = tk.Toplevel(list_window)
            update_window.title("✏️ Notu Güncelle")
            update_window.configure(bg="#f7f5f2")

            tk.Label(update_window, text="Yeni Başlık:").pack()
            title_entry = tk.Entry(update_window, width=50)
            title_entry.insert(0, note[0])  # Eski başlık
            title_entry.pack()

            tk.Label(update_window, text="Yeni İçerik:").pack()
            content_text = tk.Text(update_window, height=10, width=50)
            content_text.insert(tk.END, note[1])  # Eski içerik
            content_text.pack()

            # Kaydet butonu (iç içe fonksiyon)
            def save_updated_note():
                new_title = title_entry.get()
                new_content = content_text.get("1.0", tk.END)

                if not new_title.strip():
                    messagebox.showwarning("Uyarı", "Başlık boş olamaz.")
                    return

                # Veritabanında güncelle
                conn = sqlite3.connect("notlar.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?",
                               (new_title, new_content, selected_id))
                conn.commit()
                conn.close()

                # Listeden güncelleneni yenile
                listbox.delete(index)
                listbox.insert(index, f"🕒 (Güncellendi) | {new_title}")
                note_ids[index] = selected_id

                update_window.destroy()  # pencereyi kapat
                messagebox.showinfo("Başarılı", "Not güncellendi.")

            # Kaydet butonunu pencereye ekle
            tk.Button(update_window, text="Kaydet", command=save_updated_note).pack(pady=5)

        else:
            messagebox.showwarning("Uyarı", "Güncellemek için bir not seç.")

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
            # Yeni pencere oluşturuluyor
            detail_window = tk.Toplevel(list_window)
            detail_window.title("📝 Not Detayı")
            detail_window.configure(bg="#fff8f0")  # Arka plan sıcak pastel

            title_label = tk.Label(detail_window, text=f"Başlık: {note[0]}", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 12, "bold"))
            title_label.pack(pady=5)

            date_label = tk.Label(detail_window, text=f"Tarih: {note[2]}", bg="#fff8f0", fg="#444", font=("Segoe UI", 10))
            date_label.pack(pady=5)

            content_text = tk.Text(detail_window, wrap=tk.WORD, width=60, height=10)
            content_text.insert(tk.END, note[1])             # İçeriği metin kutusuna ekle
            content_text.config(state="disabled")            # Okunabilir ama düzenlenemez yap
            content_text.pack(padx=10, pady=10)

    listbox.bind("<Double-1>", on_note_select)               # Çift tıklama olayını bağla
    # Silme butonu ekle
    tk.Button(list_window, text="🗑️ Seçilen Notu Sil", command=delete_selected_note,
              bg="#f67280", fg="white", font=("Segoe UI", 10), padx=10).pack(pady=5)
    # Güncelle Butonu ekleme
    tk.Button(list_window, text="✏️ Seçilen Notu Güncelle", command=update_selected_note,
              bg="#6c5ce7", fg="white", font=("Segoe UI", 10), padx=10).pack(pady=5)
    # 📤 TXT dışa aktarma butonu → Tıklandığında export_notes_to_txt fonksiyonu çalışır
    tk.Button(list_window, text="📤 Notları TXT Olarak Dışa Aktar", command=export_notes_to_txt,
              bg="#00b894", fg="white", font=("Segoe UI", 10), padx=10).pack(pady=5)
    # 📤 CSV dışa aktarma butonu → Tıklandığında export_notes_to_txt fonksiyonu çalışır
    tk.Button(list_window, text="📊 Notları CSV Olarak Aktar", command=export_notes_to_csv,
              bg="#f9a825", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=5)

# Tkinter ile arayüz tasarımı
root = tk.Tk()                             # Ana pencereyi oluştur
root.configure(bg="#fff8f0")  # Arka plan: Vanilya kremi
root.title("📝 Not Defteri Uygulaması")    # Pencere başlığı

tk.Label(root, text="Başlık:", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 11)).pack()     # Başlık etiketi
title_entry = tk.Entry(root, width=50, bg="white", fg="#3e3e3e", font=("Segoe UI", 10))    # Başlık girişi
title_entry.pack()

tk.Label(root, text="İçerik:", bg="#f7f5f2", font=("Segoe UI", 11)).pack()    # İçerik etiketi
content_text = tk.Text(root, height=10, width=50, bg="white", fg="#3e3e3e", font=("Segoe UI", 10))  # İçerik kutusu
content_text.pack()

# Kaydet butonu
tk.Button(root, text="💾 Kaydet", command=save_note,
          bg="#ff6f61", fg="white", font=("Segoe UI", 10), padx=10, pady=5).pack(pady=10)

# Notları listeleme butonu
tk.Button(root, text="📋 Notları Görüntüle", command=show_notes,
          bg="#4dabf7", fg="white", font=("Segoe UI", 10), padx=10, pady=5).pack(pady=5)



root.mainloop()  # Arayüzü çalıştır
