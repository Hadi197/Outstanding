import argparse
from pathlib import Path
import sys
import pandas as pd
import os
import threading
import webbrowser
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from typing import TYPE_CHECKING

if not hasattr(pd, "DataFrame"):
    print("[!] Import pandas tidak benar. Lokasi:", getattr(pd, "__file__", "?"))
    raise SystemExit("Periksa apakah ada file bernama pandas.py atau reinstall: pip install --force-reinstall pandas")

try:
    from multipart import MultipartParser  # type: ignore  # requires python-multipart
except ImportError:
    MultipartParser = None  # fallback when lib not installed

DEFAULT_PATTERN = "PRODUKSI_REGIONAL 3 TANJUNG PERAK*.xlsx"
DEFAULT_SHEET = "TRAFFIC"

def find_excel_file(user_input: str | None) -> Path:
    """
    Jika user_input diberikan dan file ada -> pakai.
    Jika user_input berupa pattern atau tidak ditemukan -> cari dengan glob.
    """
    if user_input:
        p = Path(user_input)
        if p.is_file():
            return p
        # Treat as pattern
        matches = sorted(Path(".").glob(user_input))
        if not matches:
            print(f"[!] Tidak ditemukan file untuk input '{user_input}'.")
        else:
            if len(matches) == 1:
                print(f"[i] Menggunakan file: {matches[0]}")
                return matches[0]
            print("[!] Banyak file cocok, pilih salah satu dengan argumen eksplisit:")
            for m in matches:
                print("   -", m)
            sys.exit(1)

    # Fallback default pattern
    matches = sorted(Path(".").glob(DEFAULT_PATTERN))
    if not matches:
        print(f"[!] File tidak ditemukan. Coba letakkan file Excel sesuai pola: '{DEFAULT_PATTERN}'")
        sys.exit(1)
    if len(matches) > 1:
        print("[!] Ditemukan beberapa kandidat. Jalankan ulang dengan nama file spesifik, contoh:")
        for m in matches:
            print("   -", m)
        sys.exit(1)
    print(f"[i] Menggunakan file: {matches[0]}")
    return matches[0]

def browse_for_excel() -> Path | None:
    """
    Buka dialog pilih file (jika environment mendukung).
    """
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except Exception:
        print("[!] Modul tkinter tidak tersedia (mungkin headless).")
        return None

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Pilih File Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        print("[!] Tidak ada file dipilih.")
        return None
    print(f"[i] Dipilih: {file_path}")
    return Path(file_path)

def interactive_pick(pattern: str = "*.xlsx") -> Path | None:
    """
    List semua file Excel lalu minta user memilih via input numerik.
    """
    files = sorted(Path(".").glob(pattern))
    if not files:
        print("[!] Tidak ada file .xlsx ditemukan di folder ini.")
        return None
    print("[?] Pilih file Excel:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name}")
    while True:
        raw = input("Masukkan nomor (ENTER batal): ").strip()
        if raw == "":
            print("[!] Dibatalkan.")
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(files):
                print(f"[i] Menggunakan: {files[idx-1]}")
                return files[idx-1]
        print("[!] Input tidak valid, ulangi.")

def load_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    if sheet_name not in xl.sheet_names:
        print(f"[!] Sheet '{sheet_name}' tidak ditemukan. Sheet tersedia: {xl.sheet_names}")
        print(f"[i] Menggunakan sheet pertama: {xl.sheet_names[0]}")
        sheet_name = xl.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sheet_name, header=2)
    return df

def convert_datetime_columns(df: pd.DataFrame) -> list[str]:
    dt_cols = [c for c in df.columns if any(k in str(c).upper() for k in ("DATE", "TIME", "AT"))]
    for c in dt_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
    return dt_cols

def web_upload(timeout: int = 300) -> Path:
    """
    Menyediakan halaman web sederhana untuk upload file Excel.
    Setelah file di-upload, server berhenti dan path file dikembalikan.
    """
    upload_dir = Path(tempfile.mkdtemp(prefix="excel_upload_"))
    result = {"path": None}

    class UploadHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            html = b"""<!DOCTYPE html>
<html>
<head><title>Upload Excel</title></head>
<body>
  <h3>Upload File Excel</h3>
  <form method="POST" enctype="multipart/form-data">
    <input type="file" name="file" accept=".xlsx,.xls" required>
    <button type="submit">Upload</button>
  </form>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def do_POST(self):
            if MultipartParser is None:
                self.send_error(500, "python-multipart belum terpasang. Jalankan: pip install python-multipart")
                return
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self.send_error(400, "Content-Type tidak valid")
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                parser = MultipartParser(BytesIO(raw), content_type)
            except Exception as e:
                self.send_error(400, f"Gagal parse multipart: {e}")
                return
            file_part = None
            for part in parser.parts():
                if part.name == "file":
                    file_part = part
                    break
            if not file_part or not file_part.filename:
                self.send_error(400, "Field 'file' tidak ditemukan")
                return
            filename = Path(file_part.filename).name
            dest = upload_dir / filename
            with open(dest, "wb") as f:
                f.write(file_part.raw)
            result['path'] = dest
            resp = f"<html><body><h4>Upload sukses: {filename}</h4><p>Tutup tab ini.</p></body></html>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)

        def log_message(self, format, *args):
            return  # suppress logs

    # Cari port kosong
    server = HTTPServer(("127.0.0.1", 0), UploadHandler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"
    print(f"[i] Buka browser dan upload file di: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    def run_server():
        while result['path'] is None:
            server.handle_request()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if result['path'] is None:
        print("[!] Timeout menunggu upload.")
        sys.exit(1)
    print(f"[i] File ter-upload: {result['path']}")
    return result['path']

def manual_upload_and_browse() -> Path | None:
    """
    Menyediakan opsi untuk upload file secara manual, lalu browse file yang diunggah.
    """
    print("[?] Pilih mode:")
    print("  1. Upload file melalui web browser")
    print("  2. Browse file secara lokal")
    while True:
        choice = input("Masukkan pilihan (1/2): ").strip()
        if choice == "1":
            return web_upload()
        elif choice == "2":
            chosen = browse_for_excel()
            if not chosen:
                print("[!] Tidak ada file dipilih.")
                return None
            return chosen
        else:
            print("[!] Pilihan tidak valid, ulangi.")

def parse_args():
    p = argparse.ArgumentParser(description="Konversi kolom datetime dalam file Excel produksi.")
    p.add_argument("input", nargs="?", default=None, help="Nama file atau glob pattern input (opsional).")
    p.add_argument("output", nargs="?", default="PRODUKSI_REGIONAL3_TANJUNGPERAK_CLEAN.xlsx",
                   help="Nama file output Excel.")
    p.add_argument("--sheet", "-s", default=DEFAULT_SHEET, help="Nama sheet (default: TRAFFIC).")
    p.add_argument("--browse", "-b", action="store_true",
                   help="Buka dialog pemilihan file (GUI) untuk memilih file Excel.")
    p.add_argument("--pick", action="store_true",
                   help="Mode interaktif di terminal untuk memilih file Excel yang tersedia.")
    p.add_argument("--upload", action="store_true",
                   help="Mode web: buka halaman lokal untuk upload file Excel.")
    return p.parse_args()

def main():
    args = parse_args()

    if args.upload:
        excel_path = web_upload()
    elif args.browse:
        chosen = browse_for_excel()
        if not chosen:
            sys.exit(1)
        excel_path = chosen
    elif args.pick and not args.input:
        chosen = interactive_pick()
        if not chosen:
            sys.exit(1)
        excel_path = chosen
    elif not args.input:
        print("[?] Tidak ada input file yang diberikan.")
        excel_path = manual_upload_and_browse()
        if not excel_path:
            sys.exit(1)
    else:
        excel_path = find_excel_file(args.input)

    try:
        df = load_sheet(excel_path, args.sheet)
    except Exception as e:
        print(f"[!] Gagal membaca Excel: {e}")
        sys.exit(1)

    dt_cols = convert_datetime_columns(df)

    try:
        df.to_excel(args.output, sheet_name=args.sheet, index=False)
    except Exception as e:
        print(f"[!] Gagal menulis output: {e}")
        sys.exit(1)

    print("[OK] Selesai.")
    print("File input :", excel_path)
    print("File output:", args.output)
    print("Kolom datetime dikonversi:")
    for c in dt_cols:
        print("  -", c)

if __name__ == "__main__":
    main()
