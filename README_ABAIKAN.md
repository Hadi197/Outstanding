# Outstanding Dashboard - Fitur Abaikan

## Cara Menggunakan Fitur Abaikan

### 1. Persiapan
- Pastikan Anda berada di direktori project: `/Users/hadipurwana/Documents/PYTHON/OUTALL`
- Buka terminal untuk menjalankan server abaikan

### 2. Menjalankan Server Abaikan

```bash
# Navigasi ke direktori project
cd /Users/hadipurwana/Documents/PYTHON/OUTALL

# Jalankan server abaikan
python3 abaikan_server.py
```

Server akan berjalan di `http://localhost:8001` dan siap menerima request.

### 3. Menggunakan Fitur Abaikan di Dashboard

1. **Buka Dashboard**: Akses `outstanding.html` di browser
2. **Pilih Tab Tabel**: Klik tab "Tabel" untuk melihat data
3. **Cek Status Server**: Di bagian atas tabel, Anda akan melihat status server (hijau = aktif, merah = tidak aktif)
4. **Klik Tombol Abaikan**: Pada baris data yang ingin diabaikan, klik tombol merah "Abaikan"
5. **Konfirmasi**: Sistem akan menampilkan konfirmasi, klik "OK" untuk melanjutkan

### 4. Yang Terjadi Saat Mengabaikan Data

- **Data Disimpan**: `no_pkk_inaportnet` akan disimpan ke file `abai.csv`
- **Visual Feedback**: Baris akan diwarnai abu-abu dan tombol berubah menjadi "Diabaikan"  
- **Notifikasi**: Sistem menampilkan notifikasi sukses atau error
- **Log**: Activity akan tercatat di console server

### 5. Format File abai.csv

File `abai.csv` akan berisi:
```csv
no_pkk_inaportnet,timestamp,status
PKK.DN.2025.001,2025-10-08T10:30:00.000Z,diabaikan
PKK.LN.2025.002,2025-10-08T10:35:00.000Z,diabaikan
```

### 6. API Endpoints

Server abaikan menyediakan 2 endpoints:

- **POST /api/abaikan**: Menambah data ke abai.csv
- **GET /api/status**: Mengecek status server dan jumlah entries

### 7. Troubleshooting

#### Server Tidak Dapat Dijalankan
- Pastikan port 8001 tidak digunakan aplikasi lain
- Cek permission file dan direktori
- Pastikan Python 3 terinstall

#### Tombol Abaikan Tidak Berfungsi
- Pastikan server abaikan berjalan (cek status di dashboard)
- Cek console browser untuk error messages
- Pastikan browser tidak memblokir request localhost

#### File abai.csv Tidak Terbuat
- Cek permission write pada direktori project
- Pastikan tidak ada proses lain yang mengakses file tersebut

### 8. Keamanan dan Best Practice

- **Backup**: Backup file `abai.csv` secara berkala
- **Monitoring**: Monitor log server untuk memastikan tidak ada error
- **Access Control**: Server hanya menerima request dari localhost
- **Validation**: Semua input divalidasi sebelum disimpan

### 9. Integrasi dengan Sistem Lain

File `abai.csv` dapat diintegrasikan dengan:
- Script monitoring lainnya
- Database import/export
- Reporting tools
- Analytics dashboard

### 10. Command Line Options

```bash
# Jalankan di port custom
python3 abaikan_server.py 8002

# Default port 8001
python3 abaikan_server.py
```

---

## Struktur Project

```
OUTALL/
├── outstanding.html          # Main dashboard
├── abaikan_server.py        # Abaikan server
├── abai.csv                 # Generated file (data yang diabaikan)
├── gabung.csv               # Data utama
└── README_ABAIKAN.md        # Dokumentasi ini
```