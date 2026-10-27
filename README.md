# Dashboard Performa Media Sosial Bengkel Mahaputra 2026

Dashboard ini digunakan untuk memantau perkembangan performa
media sosial Bengkel Mahaputra menggunakan Python dan Streamlit.

## Fitur

- Total tayangan
- Total interaksi
- Kunjungan profil
- Ketukan tautan bio
- Pertumbuhan pengikut (Net Follower)
- Filter berdasarkan bulan
- Grafik performa bulanan
- Tabel data
- Insight otomatis
- Tombol untuk memuat ulang database

## Struktur File

- `app.py`: kode utama dashboard.
- `data.csv`: database performa media sosial.
- `requirements.txt`: dependensi Python.
- `README.md`: dokumentasi proyek.

## Memperbarui Data

1. Buka file `data.csv` di GitHub.
2. Klik ikon pensil untuk mengedit.
3. Tambahkan atau perbarui angka pada bulan yang diinginkan.
4. Klik Commit changes.
5. Buka dashboard Streamlit dan tekan tombol Muat Ulang Data.

## Menjalankan Secara Lokal

Instal dependensi:

```bash
pip install -r requirements.txt
```

Jalankan dashboard:

```bash
streamlit run app.py
```

## Deployment

Aplikasi dapat di-deploy melalui Streamlit Community Cloud
dengan memilih repositori GitHub ini dan file utama `app.py`.
