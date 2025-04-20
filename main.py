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

import tkinter as tk            # Tkinter modülünü GUI arayüzü oluşturmak için içe aktarıyoruz
from tkinter import messagebox  # Tkinter'in uyarı ve bilgi kutuları için olan messagebox modülünü alıyoruz
from datetime import datetime   # Tarih ve saat işlemleri için datetime modülünü içe aktarıyoruz
import sqlite3                  # SQLite veritabanı işlemleri için sqlite3 modülünü kullanacağız
from database import create_db  # Daha önce oluşturduğumuz veritabanı fonksiyonunu içeren dosyadan içe aktarım yapıyoruz

# Veritabanı yoksa oluşturulacak olan fonksiyonu hemen çağırıyoruz
create_db()  # Veritabanını oluştur

is_dark_mode = False # Tema modunu kontrol etmek için bir bayrak (açık mı koyu mu)

# Ana pencereyi global olarak tanımlıyoruz, başka fonksiyonlarda da erişebileceğiz
main_window = None  # Global pencere tanımı yapılacak

# === GİRİŞ EKRANI FONKSİYONU ===
def show_login_screen():
    login = tk.Tk()               # Yeni bir Tkinter ana penceresi oluşturulur (giriş ekranı)
    login.title("🔐 Giriş Yap")   # Pencerenin başlığı ayarlanır
    login.geometry("300x200")     # Pencere boyutu 300x200 piksel olarak belirlenir
    login.configure(bg="#fff8f0") # Arka plan rengi vanilya kremi yapılır (açık tema)

# 🧑 Kullanıcı Adı Giriş Alanı ( 👤 Kullanıcı Adı Etiketi)
    tk.Label(login, text="Kullanıcı Adı:", bg="#fff8f0").pack(pady=(30, 5)) # Üstte bir etiket yerleştir

# 👤 Kullanıcı Adı Giriş Alanı (silik yazı ile placeholder efekti)
    username_entry = tk.Entry(login, fg='grey') # Giriş kutusu oluşturulur, yazı rengi gri (silik gibi görünür)
    username_entry.insert(0, "Kullanıcı adınızı giriniz")  # İlk görünümde silik yazı görünür

    # 🔁 Kullanıcı Adı Odak Olayları
    # Kullanıcı kutuya tıkladığında silik yazı silinsin
    def on_username_focus_in(event):
        if username_entry.get() == "Kullanıcı adınızı giriniz":
            username_entry.delete(0, tk.END)
            username_entry.config(fg='black')

    # Kullanıcı kutudan çıkınca tekrar silik yazı gelmeli
    def on_username_focus_out(event):
        if username_entry.get() == "":
            username_entry.insert(0, "Kullanıcı adınızı giriniz")
            username_entry.config(fg='grey')

    # Yukarıdaki olayları giriş kutusuna bağla
    username_entry.bind("<FocusIn>", on_username_focus_in)
    username_entry.bind("<FocusOut>", on_username_focus_out)
    username_entry.pack()

    # 🔒 Şifre Giriş Alanı ( 🔑 Şifre Etiketi)
    tk.Label(login, text="Şifre:", bg="#fff8f0").pack(pady=(20, 5))    # Şifre etiketi

    # 🔑 Şifre Giriş Alanı (silik placeholder + gizli karakter)
    password_entry = tk.Entry(login, fg='grey')               # Şifre kutusu (başta düz metin olarak görünür)
    password_entry.insert(0, "Şifrenizi giriniz") # Silik yazı eklenir

    # 🔁 Şifre Giriş Odak Olayları
    # Kullanıcı kutuya tıkladığında silik yazı silinsin
    def on_password_focus_in(event):
        if password_entry.get() == "Şifrenizi giriniz":
            password_entry.delete(0, tk.END)
            password_entry.config(show="*", fg='black') # Gizli karakter (*) ile değiştir

    # Kullanıcı kutudan çıkınca tekrar silik yazı gelmeli
    def on_password_focus_out(event):
        if password_entry.get() == "":
            password_entry.insert(0, "Şifrenizi giriniz")
            password_entry.config(show="", fg='grey') # Tekrar düz yazıya dön

    # Yukarıdaki olayları giriş kutusuna bağla
    password_entry.bind("<FocusIn>", on_password_focus_in)
    password_entry.bind("<FocusOut>", on_password_focus_out)
    password_entry.pack()

    # ✅ Şifre kontrol fonksiyonu
    def check_password():
        username = username_entry.get()
        password = password_entry.get()
        if username == "admin" and password == "root": # Sabit kullanıcı ve şifre kontrolü
            messagebox.showinfo("Başarılı", "Giriş başarılı!") # Giriş başarılı ise mesaj göster
            login.destroy()  # Giriş penceresini kapat
            open_main_window()  # Ana pencereyi aç
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")# Hatalı giriş uyarısı

    tk.Button(login, text="Giriş", command=check_password, bg="#6c5ce7", fg="white").pack(pady=20) # Giriş butonu
    login.bind("<Return>", lambda event: check_password())   # ⏎ Enter tuşuna basıldığında giriş yapılır
    login.mainloop() # Giriş ekranı döngüsü başlatılır

# === ANA UYGULAMA PENCERESİ ===
# 📝 Ana uygulama penceresini oluşturur ve tüm arayüz bileşenlerini yerleştirir
def open_main_window():
    global main_window, title_entry, content_text, title_label, content_label, save_button, show_button, theme_button

    main_window = tk.Tk()                # 🌟 Yeni bir Tkinter ana penceresi oluştur
    main_window.title("📝 Not Defteri")  # 🏷️ Pencerenin başlığını belirle
    main_window.configure(bg="#fff8f0")  # 🎨 Arka plan rengini açık pastel ton olarak ayarla

    # 📌 Başlık etiketi (label)
    title_label = tk.Label(main_window, text="Başlık:", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 11))
    title_label.pack() # 📦 Ekrana yerleştir

    # ✏️ Başlık girişi (Entry) + silik açıklama (placeholder)
    title_entry = tk.Entry(main_window, width=50, fg='grey')   # 📥 Gri renkte yazı ile placeholder
    title_entry.insert(0, "Başlık giriniz")    # 📋 Varsayılan metin ekle

    # 🔁 Başlık girişi Odak Olayları
    # Kullanıcı kutuya tıkladığında silik yazı silinsin
    def on_title_focus_in(event):
        if title_entry.get() == "Başlık giriniz":
            title_entry.delete(0, tk.END)  # 🔄 Alanı temizle
            title_entry.config(fg='black') # 🎨 Yazı rengini siyah yap

    # Kullanıcı kutudan çıkınca tekrar silik yazı gelmeli
    def on_title_focus_out(event):
        if title_entry.get() == "":
            title_entry.insert(0, "Başlık giriniz")  # 🔁 Boşsa tekrar yaz
            title_entry.config(fg='grey') # 🎨 Yazı rengini gri yap

    # Yukarıdaki olayları giriş kutusuna bağla
    title_entry.bind("<FocusIn>", on_title_focus_in)    # 🎯 Odaklandığında çalışacak
    title_entry.bind("<FocusOut>", on_title_focus_out)  # ➡️ Odak kaybında çalışacak
    title_entry.pack()

    # 📌 İçerik etiketi
    content_label = tk.Label(main_window, text="İçerik:", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 11))
    content_label.pack()

    # 🧾 İçerik girişi (Text) + silik açıklama
    content_text = tk.Text(main_window, height=10, width=50, fg='grey') # 📥 Çok satırlı metin alanı
    content_text.insert("1.0", "Notunuzu yazınız")   # 📋 Varsayılan metin

    # 🔁 İçerik girişi Odak Olayları
    # Kullanıcı kutuya tıkladığında silik yazı silinsin
    def on_content_focus_in(event):
        if content_text.get("1.0", tk.END).strip() == "Notunuzu yazınız":
            content_text.delete("1.0", tk.END) # 🔄 Alanı temizle
            content_text.config(fg='black') # 🎨 Yazı rengini siyah yap

    # Kullanıcı kutudan çıkınca tekrar silik yazı gelmeli
    def on_content_focus_out(event):
        if content_text.get("1.0", tk.END).strip() == "":
            content_text.insert("1.0", "Notunuzu yazınız") # 🔁 Boşsa tekrar yaz
            content_text.config(fg='grey') # 🎨 Yazı rengini gri yap

    # Yukarıdaki olayları giriş kutusuna bağla
    content_text.bind("<FocusIn>", on_content_focus_in)
    content_text.bind("<FocusOut>", on_content_focus_out)
    content_text.pack()

    # 💾 Notu kaydeden buton
    save_button = tk.Button(main_window, text="💾 Kaydet", command=save_note, bg="#ff6f61", fg="white")
    save_button.pack(pady=10)

    # 📋 Notları listeleyen buton
    show_button = tk.Button(main_window, text="📋 Notları Görüntüle", command=show_notes, bg="#4dabf7", fg="white")
    show_button.pack()

    # 🌙 Temayı değiştiren buton
    theme_button = tk.Button(main_window, text="🌙 Koyu Tema", command=toggle_theme, bg="#555", fg="white")
    theme_button.pack(pady=5)

    # 💡 Ctrl+S ile hızlı kaydetme tuşu
    main_window.bind("<Control-s>", lambda event: save_note())  # ⌨️ Ctrl+S ile kaydet

    main_window.mainloop()  # 🌀 Arayüz döngüsünü başlat (uygulamayı çalıştır)

# === KAYDETME ===
# 💾 Kullanıcının yazdığı notu veritabanına kaydeden fonksiyon
def save_note():
    title = title_entry.get()  # 📝 Başlık giriş kutusundaki değeri al
    content = content_text.get("1.0", tk.END)  # 📄 İçerik kutusundaki metni al (1. satırdan sona kadar)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ⏱️ Notun oluşturulma tarihini ve saatini al

    # 🚫 Başlık boşsa uyarı ver ve işlemi durdur
    if not title.strip():
        messagebox.showwarning("Uyarı", "Başlık boş olamaz.") # ⚠️ Kullanıcıya uyarı mesajı göster
        return

    # 💽 Veritabanı bağlantısını aç
    conn = sqlite3.connect("notlar.db")
    cursor = conn.cursor()

    # 🧾 Veritabanına notu ekle (title, content, created_at alanlarına)
    cursor.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, created_at))
    conn.commit()  # ✅ Değişiklikleri kaydet
    conn.close()   # 🔒 Bağlantıyı kapat

    messagebox.showinfo("Başarılı", "Not kaydedildi!")  # ✅ Kullanıcıya başarı mesajı göster

    # 🧹 Giriş alanlarını temizle
    title_entry.delete(0, tk.END)        # Başlık kutusunu boşalt
    content_text.delete("1.0", tk.END) # İçerik kutusunu boşalt

# === TEMA DEĞİŞTİRME ===
# 🌗 Tema değiştirme fonksiyonu (Açık <-> Koyu tema arasında geçiş yapar)
def toggle_theme():
    global is_dark_mode # 🌍 Tema durumunu takip eden global değişkeni içe aktar

    # ☀️ Eğer şu an koyu tema aktifse → açık temaya geç
    if is_dark_mode:
        main_window.configure(bg="#fff8f0") # Ana pencereyi açık tema rengine getir

        title_label.config(bg="#fff8f0", fg="#6b4c9a")   # Başlık etiketi: pastel zemin, eflatun yazı
        content_label.config(bg="#fff8f0", fg="#6b4c9a") # İçerik etiketi aynı şekilde güncellenir

        title_entry.config(bg="white", fg="#3e3e3e")     # Giriş kutuları: beyaz zemin, koyu gri yazı
        content_text.config(bg="white", fg="#3e3e3e")

        save_button.config(bg="#ff6f61", fg="white")     # Kaydet butonu: mercan kırmızısı
        show_button.config(bg="#4dabf7", fg="white")     # Görüntüle butonu: buz mavisi
        theme_button.config(text="🌙 Koyu Tema")         # Tema butonunun yazısını güncelle

        is_dark_mode = False # Durumu açık tema olarak güncelle

    # 🌑 Şu an açık temadaysa → koyu temaya geç
    else:
        main_window.configure(bg="#2c2c2c")  # Arka planı koyu gri yap

        title_label.config(bg="#2c2c2c", fg="#f1c40f")    # Etiketler: koyu zemin, sarı yazı
        content_label.config(bg="#2c2c2c", fg="#f1c40f")

        title_entry.config(bg="#3c3c3c", fg="white")      # Giriş kutuları: koyu gri, beyaz yazı
        content_text.config(bg="#3c3c3c", fg="white")

        save_button.config(bg="#8e44ad", fg="white")      # Kaydet butonu: koyu mor
        show_button.config(bg="#3498db", fg="white")      # Görüntüle butonu: açık mavi
        theme_button.config(text="☀️ Açık Tema")          # Butonun yazısını açık temaya çevir

        is_dark_mode = True # Durumu koyu tema olarak güncelle


# === NOTLARI GÖSTER ===
# 📋 Kayıtlı notları gösteren pencereyi açar
def show_notes():
    list_window = tk.Toplevel()  # Yeni bir pencere (popup) oluştur
    list_window.title("📋 Kayıtlı Notlar")  # Pencere başlığı
    list_window.configure(bg="#fff8f0")  # Arka planı pastel vanilya rengine ayarla

    # 🔍 ARAMA KUTUSU VE BUTONU EKLENİYOR START
    search_frame = tk.Frame(list_window, bg="#fff8f0") # Arama kutusu ve buton için yatay bir çerçeve oluştur
    search_frame.pack(pady=5) # Çerçeveyi pencereye yerleştir (üstte olacak)

    # Arama kutusu başlığı (etiket)
    tk.Label(search_frame, text="🔎 Başlıkta Ara:", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

    search_entry = tk.Entry(search_frame, width=30, bg="white", fg="#3e3e3e", font=("Segoe UI", 10)) # Kullanıcının arama yapacağı giriş kutusu
    search_entry.pack(side=tk.LEFT, padx=5) # Kutuyu çerçeveye sola hizalı ekle
    # 🔎 Arama Kutusu Oluştur END

    # 🔄 ARAMA İŞLEVİNİ YAPAN FONKSİYON (🔍 Arama Fonksiyonu (İç Fonksiyon)
    def search_notes():
        keyword = search_entry.get().lower()  # Kullanıcının yazdığı metni al, küçük harfe çevir
        listbox.delete(0, tk.END)        # Mevcut liste temizleniyor (Liste kutusunu temizle)
        note_ids.clear()                      # Daha önceki ID listesi de temizleniyor

        # Notlar listesinde arama yap
        for i, note in enumerate(notes):              # notes: veritabanından çekilen tüm notlar
            note_id, title, content, created_at = note
            if keyword in title.lower(): # Başlık içinde aranan kelime var mı kontrol et - Arama kelimesi başlıkta geçiyor mu?
                listbox.insert(tk.END, f"🕒 {created_at} | {title}")  # Uyan başlığı listeye ekle
                note_ids.append(note_id)  # Uyumlu notun ID’sini de notlar listesine ekle

    # 🔍 Ara butonu, tıklanınca arama fonksiyonunu çalıştırır
    tk.Button(search_frame, text="Ara", command=search_notes,
              bg="#6b4c9a", fg="white", font=("Segoe UI", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)
    # "Ara" butonuna klavye kısayolu (Ctrl+F)
    list_window.bind("<Control-f>", lambda event: search_entry.focus_set()) #"Ara" butonuna klavye kısayolu (Ctrl+F)

    # 📤 NOTLARI .TXT DOSYASINA DIŞA AKTARAN FONKSİYON
    def export_notes_to_txt():
        # 💾 Veritabanına bağlanıyoruz
        conn = sqlite3.connect("notlar.db")  # 💽 Veritabanına bağlan
        cursor = conn.cursor()

        # 📦 Tüm notları tarih sırasına göre çekiyoruz
        cursor.execute("SELECT title, content, created_at FROM notes ORDER BY created_at DESC")
        all_notes = cursor.fetchall()   # 📋 Tüm notları al
        conn.close()  # 🔐 Bağlantıyı kapatıyoruz

        # ❗ Hiç not yoksa kullanıcıya bilgi ver
        if not all_notes:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak not bulunamadı." , parent=list_window)
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
        messagebox.showinfo("Başarılı", "Notlar 'notlar_export.txt' dosyasına başarıyla aktarıldı." , parent=list_window)

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
            messagebox.showinfo("Bilgi", "Dışa aktarılacak not bulunamadı." , parent=list_window)
            return

        # 📁 CSV dosyasını yazmak için açıyoruz
        with open("notlar_export.csv", "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Tarih", "Başlık", "İçerik"]) # 🧱 Başlık satırını yaz

            # 🧾 Notları satır satır yaz
            for note in all_notes:
                title, content, created_at = note
                writer.writerow([created_at, title, content]) # 📤 Her bir notu satır olarak yaz

        # ✅ Kullanıcıya bilgilendirme
        messagebox.showinfo("Başarılı", "Notlar 'notlar_export.csv' dosyasına başarıyla aktarıldı." , parent=list_window)


# 📜 𝐋𝐈𝐒𝐓𝐁𝐎𝐗 & 𝐒𝐂𝐑𝐎𝐋𝐋𝐁𝐀𝐑: Notları Listeleme Bölümü
    # 📌 Başlık: Listeleme Alanı & Scrollbar Oluşturma
    list_window.title("📋 Kayıtlı Notlar") # Pencerenin başlığını ayarla

    scrollbar = tk.Scrollbar(list_window)  # 📎 Dikey kaydırma çubuğu oluştur
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # Sağ tarafa yerleştir, dikey olarak doldur

    # 📜 Notları gösterecek kutu oluşturuluyor
    listbox = tk.Listbox(
        list_window,                  # Kapsayıcı pencere
        width=80,                     # Genişlik
        height=15,                    # Yükseklik (satır sayısı)
        yscrollcommand=scrollbar.set, # Kaydırma çubuğuna bağla
        bg="white",                   # Arka plan rengi
        fg="#3e3e3e",                 # Yazı rengi
        font=("Segoe UI", 10),        # Yazı tipi ve boyutu
        selectbackground="#ffe066",   # Seçili satır arka plan rengi
        selectforeground="#000")      # Seçili satır yazı rengi

    listbox.pack(padx=10, pady=10)    # Liste kutusunu yerleştir

    scrollbar.config(command=listbox.yview) # Kaydırma çubuğunu listbox'a bağla

    # 📌 Başlık: Veritabanı Bağlantısı & Notları Çekme
    conn = sqlite3.connect("notlar.db")  # 💽 Veritabanına bağlan
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")  # Tüm notları çek
    # 🔍 Notları id, başlık, içerik ve tarih olarak al → en yeni en üstte

    notes = cursor.fetchall() # 📦 Tüm notları liste olarak getir
    conn.close()              # 🔐 Bağlantıyı kapat

    #🆔 𝐋𝐈𝐒𝐓𝐄𝐘𝐄 𝐄𝐊𝐋𝐄𝐌𝐄: Notları Arayüze Aktar
    note_ids = []  # 📌 Her satıra karşılık gelen ID’leri saklayan liste (silme/güncelleme için lazım)

    # 🔁 Tüm notları sırayla listbox'a ekle
    for note in notes:  # Her not için satır ekle
        note_id, title, content, created_at = note  # 🪪 Veritabanından gelen sütunlar
        listbox.insert(tk.END, f"🕒 {created_at} | {title}")   # 📝 Notu listeye yaz
        note_ids.append(note_id) # 🆔 ID'yi ayrı listede sakla - ID'leri sırayla listeye kaydet

    # 🗑️ Seçilen notu silen fonksiyon
    def delete_selected_note():
        selection = listbox.curselection()  # ✅ Kullanıcının listeden seçtiği satırı al
        if selection:                       # ⛔ Eğer hiçbir şey seçilmediyse işlem yapma
            index = selection[0]            # 🔢 Seçilen notun listedeki sırası (index)
            selected_id = note_ids[index]   # 🆔 Seçilen notun veritabanı ID’si

            # ❓ Silme işlemi için onay al
            confirm = messagebox.askyesno("Onay", "Bu notu silmek istediğine emin misin?", parent=list_window)
            if confirm:
                # 💾 Veritabanından notu sil
                conn = sqlite3.connect("notlar.db")
                cursor = conn.cursor()
                # ❌ Seçilen notu ID’ye göre sil
                cursor.execute("DELETE FROM notes WHERE id = ?", (selected_id,))
                conn.commit()
                conn.close()

                # 🗑️ Listeden de kaldır
                listbox.delete(index) # Listbox’tan kaldır
                note_ids.pop(index)   # ID listesinden çıkar

                # ✅ Bilgilendirme mesajı göster
                messagebox.showinfo("Silindi", "Not başarıyla silindi.", parent=list_window)
        else:
            # ⚠️ Hiçbir not seçilmemişse uyarı göster
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir not seç." , parent=list_window)

    # ✏️ Seçilen notu güncelleme fonksiyonu
    def update_selected_note():
        selection = listbox.curselection()  # ✅ Seçili not satırını al
        if selection:                       # ⛔ Hiçbir şey seçilmemişse işlem yapılmaz
            index = selection[0]            # 🔢 Seçilen öğenin listbox'taki index’i
            selected_id = note_ids[index]   # 🆔 O öğenin veritabanı ID’si

            # 💾 Notu veritabanından getir
            conn = sqlite3.connect("notlar.db")
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM notes WHERE id = ?", (selected_id,))
            note = cursor.fetchone()
            conn.close()

            # ✨ Güncelleme penceresi oluştur - Yeni pencere oluştur (güncelleme ekranı)
            update_window = tk.Toplevel(list_window)
            update_window.title("✏️ Notu Güncelle")
            update_window.configure(bg="#f7f5f2")

            # 🔑 Escape tuşu → pencereyi kapatır - ⌨️ Tuşlarla kontrol (Escape ile kapat)
            update_window.bind("<Escape>", lambda event: update_window.destroy())   # 🔐 ESC ile kapat
            # update_window.bind("<Control-s>", lambda event: save_updated_note())    # 💾 Ctrl+S → Kaydet

            # 🖊️ Yeni Başlık etiketi ve giriş alanı
            tk.Label(update_window, text="Yeni Başlık:").pack()
            title_entry = tk.Entry(update_window, width=50)
            title_entry.insert(0, note[0])    # ✏️ Eski başlığı getir
            title_entry.pack()
            # title_entry.focus()  # 🔍 İmleç bu alanda otomatik belirsin - Güncelleme penceresi açıldığında imleç burada olsun
            title_entry.focus_set()  # ✨ Ekran açıldığında imleç burada olacak

            # 📝 Yeni İçerik etiketi ve metin alanı
            tk.Label(update_window, text="Yeni İçerik:").pack()
            content_text = tk.Text(update_window, height=10, width=50)
            content_text.insert(tk.END, note[1])    # 📄 Eski içeriği getir
            content_text.pack()

            # 💾 KAYDETME ALT FONKSİYONU : Güncellenmiş notu veritabanına kaydet -
            def save_updated_note():

                new_title = title_entry.get()
                new_content = content_text.get("1.0", tk.END)

                if not new_title.strip():
                    messagebox.showwarning("Uyarı", "Başlık boş olamaz.")
                    return

                # 💾 Veritabanında güncelle
                conn = sqlite3.connect("notlar.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?",
                               (new_title, new_content, selected_id))
                conn.commit()
                conn.close()

                # ⏰ Güncellenen tarih listede güncelle
                updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 🔁 Listbox güncelle
                listbox.delete(index)
                listbox.insert(index, f"🕒 {updated_time} | {new_title}")
                note_ids[index] = selected_id

                update_window.destroy()  #  🔐 pencereyi kapat
                messagebox.showinfo("Başarılı", "Not güncellendi." , parent=list_window)

            # 💾 Kaydet butonu
            tk.Button(update_window, text="Kaydet", command=save_updated_note).pack(pady=5)

            # 🎹 Tuş ile işlemler (Enter: kaydet, ESC: kapat)
            update_window.bind("<Escape>", lambda event: update_window.destroy()) # ESC → pencereyi kapat
            # update_window.bind("<Return>", lambda event: save_updated_note())
            """
             # Ctrl + Enter → notu kaydet
            def ctrl_enter_check(event):
                if (event.state & 0x4) and event.keysym == "Return":  # Ctrl tuşu basılı + Enter
                    save_updated_note()

            update_window.bind("<Key>", ctrl_enter_check)
            
            """
            # Güncelleme penceresi oluşturulduktan hemen sonra TUŞ ATAMALARI YAPILMALI ⬇️
            # Tuşlarla işlem (Enter: kaydet, ESC: kapat)
            # ⌨️ Tuşlar ile işlem yapılabilmesi için:
        else:
            # ⚠️ Seçim yapılmadıysa kullanıcıyı uyar
            messagebox.showwarning("Uyarı", "Güncellemek için bir not seç." , parent=list_window)

    # 📄 Fonksiyon: Seçilen notun detaylarını göster (çift tıklama ile)
    def on_note_select(event):
        selection = listbox.curselection()  # 🖱️ Kullanıcının seçtiği notu al
        if selection:                       # 🛑 Eğer bir not seçilmişse devam et
            index = selection[0]            # 📌 Seçilen notun index’i (sıra no)
            selected_id = note_ids[index]   # 🆔 Veritabanındaki ID’yi al

            # 💾 Notun detaylarını veritabanından çek
            conn = sqlite3.connect("notlar.db")              # Veritabanına tekrar bağlan
            cursor = conn.cursor()
            cursor.execute("SELECT title, content, created_at FROM notes WHERE id = ?", (selected_id,))
            note = cursor.fetchone()
            conn.close()

            # 📖 Yeni pencere aç → Detayları göster
            detail_window = tk.Toplevel(list_window)
            detail_window.title("📝 Not Detayı")
            detail_window.configure(bg="#fff8f0")  # Arka plan sıcak pastel

            # 🏷️ Başlık etiketi
            title_label = tk.Label(detail_window, text=f"Başlık: {note[0]}", bg="#fff8f0", fg="#6b4c9a", font=("Segoe UI", 12, "bold"))
            title_label.pack(pady=5)

            # ⏰ Tarih etiketi
            date_label = tk.Label(detail_window, text=f"Tarih: {note[2]}", bg="#fff8f0", fg="#444", font=("Segoe UI", 10))
            date_label.pack(pady=5)

            # 📝 İçerik alanı
            content_text = tk.Text(detail_window, wrap=tk.WORD, width=60, height=10)
            content_text.insert(tk.END, note[1])             # 🧾 Notun içeriği
            content_text.config(state="disabled")            # 🛑 Sadece okunabilir, düzenlenemez
            content_text.pack(padx=10, pady=10)

            # 🔐 ESC → pencereyi kapat
            detail_window.bind("<Escape>", lambda event: detail_window.destroy())

            # 📋 Ctrl+C → metni panoya kopyala
            def copy_to_clipboard(event=None):
                detail_window.clipboard_clear()         # 🧹 Önce panoyu temizle
                detail_window.clipboard_append(note[1]) # 📝 İçeriği panoya ekle
                messagebox.showinfo("Kopyalandı", "İçerik panoya kopyalandı.", parent=detail_window)

            detail_window.bind("<Control-c>", copy_to_clipboard) # ⌨️ Ctrl + C → kopyala

    listbox.bind("<Double-1>", on_note_select)  # 👆 Çift tıklanınca detay penceresi açılır

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

    # --- ⌨️ Klavye kısayolları ---
    search_entry.focus_set()  # 📌 Pencere açılır açılmaz imleç arama kutusunda olur
    list_window.bind("<Control-f>", lambda event: search_entry.focus_set())  # 🔍 Ctrl+F → Arama kutusuna odaklan
    list_window.bind("<Escape>", lambda event: list_window.destroy())        # ❌ ESC → pencereyi kapat

# === UYGULAMAYI BAŞLAT ===
show_login_screen()
