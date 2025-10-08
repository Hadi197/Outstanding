# 🔧 Panduan Konfigurasi GitHub Token untuk Outstanding Dashboard

## 📋 Masalah Saat Ini

Data abaikan saat ini disimpan di **localStorage browser** karena GitHub token tidak memiliki akses yang tepat ke repository.

### ❌ Error yang Terjadi:
```
Repository access failed: 404
Token valid for user: Hadi197
File access failed: 404
Write permissions failed: 404
```

## 🔐 Solusi: Membuat GitHub Token Baru

### 1. Akses GitHub Token Settings
1. Buka [GitHub.com](https://github.com)
2. Klik profile picture → **Settings**
3. Scroll ke bawah → **Developer settings**
4. Klik **Personal access tokens** → **Tokens (classic)**

### 2. Generate New Token
1. Klik **Generate new token** → **Generate new token (classic)**
2. Isi **Note**: `Outstanding Dashboard Token`
3. Atur **Expiration**: `90 days` atau `No expiration`

### 3. ✅ Pilih Scope yang Benar
Centang scope berikut:
- ✅ **repo** (Full control of private repositories)
  - ✅ repo:status
  - ✅ repo_deployment
  - ✅ public_repo
  - ✅ repo:invite
  - ✅ security_events
- ✅ **workflow** (Update GitHub Action workflows)

### 4. Generate dan Copy Token
1. Klik **Generate token**
2. **COPY** token yang dihasilkan (tidak akan ditampilkan lagi!)
3. Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 🔄 Update Token di Aplikasi

### Metode 1: Update di Netlify Functions
1. Edit file `/netlify/functions/abaikan.js`
2. Ganti baris:
```javascript
const GITHUB_TOKEN = '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';
```
Dengan token baru:
```javascript
const GITHUB_TOKEN = 'ghp_your_new_token_here';
```

### Metode 2: Environment Variables (Recommended)
1. Di Netlify dashboard:
   - Site settings → Environment variables
   - Add: `GITHUB_TOKEN` = `ghp_your_new_token_here`
2. Update code untuk menggunakan env var:
```javascript
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'fallback_token';
```

## 🧪 Test Koneksi

Jalankan test script:
```bash
node test-github.js
```

Output yang diharapkan:
```
✅ Token valid for user: Hadi197
✅ Repository access: OK
✅ File exists: abai.csv
✅ Write permissions: OK
```

## 📱 Hasil Setelah Konfigurasi

### Sebelum:
- ❌ Data disimpan di localStorage browser
- ❌ Hilang jika cache dihapus
- ❌ Tidak sinkron antar device

### Sesudah:
- ✅ Data disimpan di GitHub repository
- ✅ Permanen dan tersinkron
- ✅ Accessible dari mana saja
- ✅ Backup otomatis

## 🔍 Troubleshooting

### Error 404: Not Found
- Token tidak memiliki akses ke repository
- **Solusi**: Pastikan scope `repo` dicentang

### Error 403: Forbidden
- Token tidak memiliki permission write
- **Solusi**: Regenerate token dengan scope yang tepat

### Error 401: Unauthorized
- Token expired atau invalid
- **Solusi**: Generate token baru

## 📞 Support

Jika masih ada masalah:
1. Pastikan repository `Hadi197/Outstanding` accessible
2. Cek token expiration date
3. Verifikasi scope permissions
4. Test dengan `test-github.js`

---
📅 Updated: October 8, 2025
🔗 Repository: https://github.com/Hadi197/Outstanding