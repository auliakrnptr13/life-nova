# Lumacta 🌿
**Platform Aktuaria Endowment & Kontinyu**

## Cara menjalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cara deploy ke Streamlit Community Cloud (gratis)

1. Upload semua file ini ke GitHub (repo baru)
2. Buka https://share.streamlit.io
3. Login dengan GitHub
4. Klik **New app** → pilih repo → pilih `app.py`
5. Klik **Deploy** — selesai! Web langsung online

## Struktur file

```
lumacta/
├── app.py          ← file utama (jalankan ini)
├── database.py     ← sistem login & penyimpanan data
├── styles.py       ← tema warna pink-hijau
├── requirements.txt
└── README.md
```

## Fitur yang sudah jadi
- [x] Register akun (nama, email, username, password)
- [x] Login dengan email atau username
- [x] Dashboard personal per user
- [x] Riwayat perhitungan tersimpan otomatis
- [x] Tema pink-hijau kustom

## Fitur berikutnya (modul kalkulator)
- [ ] Simulasi premi tabungan berjangka (endowment)
- [ ] Bandingkan dua jenis asuransi (diskrit vs kontinyu)
- [ ] Peluang hidup (survival analysis)
- [ ] Unduh laporan PDF
