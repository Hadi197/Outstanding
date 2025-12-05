# 🔧 Cara Test Keterangan Feature

## ⚠️ PENTING: Keterangan TIDAK AKAN TERSIMPAN jika tidak mengikuti langkah ini!

---

## 📍 Pilih Method Testing:

### Method 1: Development Mode (RECOMMENDED untuk testing)

#### Step 1: Start Local Server
```bash
cd /Users/hadipurwana/Documents/PYTHON/OUTALL
python3 abaikan_server.py
```

**Output yang benar:**
```
🚀 Abaikan Server berjalan di http://localhost:8001
📁 CSV file: /Users/hadipurwana/Documents/PYTHON/OUTALL/abai.csv
📌 Endpoints:
   POST /api/abaikan - Tambah data ke abai.csv
   POST /api/keterangan - Save keterangan
   GET  /api/keterangan - Get all keterangan
   GET  /api/status  - Cek status server
⏹️  Tekan Ctrl+C untuk berhenti
```

#### Step 2: Start Simple HTTP Server (Terminal BARU)
```bash
cd /Users/hadipurwana/Documents/PYTHON/OUTALL
python3 -m http.server 8000
```

#### Step 3: Buka di Browser
```
http://localhost:8000/outstanding.html
```

**JANGAN** double-click file `outstanding.html` langsung!
**HARUS** buka via `http://localhost:8000`

#### Step 4: Test Save Keterangan
1. Buka DevTools (F12) → Tab Console
2. Klik tombol "Tambah Keterangan" pada data PKK
3. Input keterangan, klik "Simpan"
4. Lihat di Console harus ada:
   ```
   🚀 Saving keterangan to GitHub: {pkk: "...", ...}
   ✅ Keterangan saved to keterangan.csv via server
   ```
5. Check file `keterangan.csv` - data harus bertambah!

---

### Method 2: Production Mode (Netlify)

#### Pre-requisites:
- Deploy ke Netlify
- Set Environment Variable: `GITHUB_TOKEN` dengan Personal Access Token dari GitHub
- Token harus punya permission: `repo` (full control of private repositories)

#### Testing di Production:
1. Buka URL Netlify (contoh: `https://your-app.netlify.app`)
2. Klik "Tambah Keterangan"
3. Input keterangan, klik "Simpan"
4. Lihat Console, harus ada:
   ```
   🚀 Saving keterangan to GitHub: ...
   📡 Response: 200 {success: true, ...}
   ✅ Keterangan saved to GitHub: ...
   🔄 Reloading keterangan from GitHub...
   📖 handleGetKeterangan: Reading from GitHub...
   ✅ Loaded X keterangan from GitHub
   ```
5. Data tersimpan langsung ke GitHub repository file `keterangan.csv`

---

## 🐛 Troubleshooting

### Problem: "❌ Server tidak aktif! Jalankan: python3 abaikan_server.py"
**Cause**: Local server belum jalan
**Solution**: Run `python3 abaikan_server.py` di terminal

### Problem: "❌ Gagal menyimpan ke GitHub"
**Cause**: 
- Di localhost: Server belum jalan
- Di Netlify: GITHUB_TOKEN tidak di-set atau invalid

**Solution**:
- Localhost: Start server (lihat Method 1)
- Netlify: Check Environment Variables di Netlify Dashboard

### Problem: Data tersimpan tapi hilang setelah refresh
**Cause**: Browser cache atau file tidak ter-reload
**Solution**: 
- Hard refresh: Ctrl+Shift+R (Windows/Linux) atau Cmd+Shift+R (Mac)
- Clear browser cache
- Restart server dan reload page

### Problem: CORS Error
**Cause**: Buka file dengan `file://` protocol (double-click)
**Solution**: HARUS buka via HTTP server (`http://localhost:8000`)

---

## ✅ Verification Checklist

- [ ] Server `abaikan_server.py` running (Development mode)
- [ ] Buka via `http://localhost:8000` (BUKAN `file://`)
- [ ] DevTools Console tidak ada error merah
- [ ] Setelah save, muncul notifikasi hijau "✅ Keterangan tersimpan"
- [ ] File `keterangan.csv` bertambah data baru
- [ ] Setelah refresh page, keterangan tetap muncul
- [ ] Tombol berubah dari "Tambah Keterangan" (biru) ke "Edit Keterangan" (hijau)

---

## 📝 Quick Test Commands

```bash
# Terminal 1: Start backend server
cd /Users/hadipurwana/Documents/PYTHON/OUTALL
python3 abaikan_server.py

# Terminal 2: Start HTTP server  
cd /Users/hadipurwana/Documents/PYTHON/OUTALL
python3 -m http.server 8000

# Terminal 3: Test endpoint (optional)
curl -X POST http://localhost:8001/api/keterangan \
  -H "Content-Type: application/json" \
  -d '{"pkk":"TEST.PKK","pkk_inaportnet":"TEST.INAPORTNET","keterangan":"Test save"}'

# Check CSV content
cat keterangan.csv
```

---

## 🔍 Debug Mode

Add `?github=true` ke URL untuk force production mode:
```
http://localhost:8000/outstanding.html?github=true
```
Ini akan gunakan Netlify Function path (akan fail di localhost karena no Netlify Functions)

---

**Last Updated**: December 5, 2025
