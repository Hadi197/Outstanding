# /Users/hadipurwana/Documents/PYTHON/OUT ALL/lookup.py
import argparse
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz


def resolve_path(p: str | None, default_names: list[str], search_dir: Path) -> Path:
    if p:
        cand = Path(p)
        if cand.exists():
            return cand
        # Try relative to search_dir
        cand2 = (search_dir / p).resolve()
        if cand2.exists():
            return cand2
        print(f"Error: File not found: {p}", file=sys.stderr)
        sys.exit(1)

    # Try defaults (case-insensitive search)
    lower_defaults = {n.lower() for n in default_names}
    for f in search_dir.iterdir():
        if f.is_file() and f.name.lower() in lower_defaults:
            return f.resolve()

    print(f"Error: Could not locate any of: {', '.join(default_names)} in {search_dir}", file=sys.stderr)
    sys.exit(1)


def pick_column(df: pd.DataFrame, wanted: str) -> str:
    # Return a column name matching wanted (case-insensitive, spaces/underscores ignored)
    def norm(s: str) -> str:
        return ''.join(ch for ch in s.lower() if ch.isalnum())

    target = norm(wanted)
    for col in df.columns:
        if norm(col) == target:
            return col
    # Also try common variants
    variants = {
        'nomor_pkk': ['no_pkk', 'nomor pkk', 'no pkk', 'no_pkk_inaportnet', 'pkk'],
        'no_pkk_inaportnet': ['no_pkk', 'nomor_pkk', 'pkk_inaportnet', 'pkk'],
    }
    for alt in variants.get(wanted, []):
        t = norm(alt)
        for col in df.columns:
            if norm(col) == t:
                return col
    print(f"Error: Kolom '{wanted}' tidak ditemukan di dataframe. Kolom tersedia: {list(df.columns)}", file=sys.stderr)
    sys.exit(1)


def normalize_key_series(s: pd.Series) -> pd.Series:
    # Treat as string keys; strip whitespace
    return s.astype(str).str.strip()


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    data_dir = here  # Path to current directory (root)

    parser = argparse.ArgumentParser(
        description="Gabungkan SPB.csv, wasop.csv, dan lhgk.csv."
    )
    parser.add_argument("--spb", help="Path ke SPB.csv (default: cari di folder data)")
    parser.add_argument("--wasop", help="Path ke wasop.csv (default: cari di folder data)")
    parser.add_argument("--lhgk", help="Path ke lhgk.csv (default: cari di folder data)")
    parser.add_argument("--how", choices=["left", "right", "inner", "outer"], default="left",
                        help="Tipe merge (default: left, WASOP sebagai referensi)")
    parser.add_argument("--output", "-o", help="Path output CSV (default: gabung.csv di root folder)")
    args = parser.parse_args(argv)

    spb_path = resolve_path(args.spb, ["SPB.csv", "spb.csv"], data_dir)
    wasop_path = resolve_path(args.wasop, ["wasop.csv", "WASOP.csv"], data_dir)
    lhgk_path = resolve_path(args.lhgk, ["lhgk.csv", "LHGK.csv"], data_dir)
    out_path = Path(args.output) if args.output else (data_dir / "gabung.csv")

    print(f"Memuat SPB: {spb_path}")
    print(f"Memuat WASOP: {wasop_path}")
    print(f"Memuat LHGK: {lhgk_path}")

    # Load as string to preserve PKK formatting
    spb = pd.read_csv(spb_path, dtype=str, keep_default_na=False)
    wasop = pd.read_csv(wasop_path, dtype=str, keep_default_na=False)
    lhgk = pd.read_csv(lhgk_path, dtype=str, keep_default_na=False)

    print(f"Baris SPB: {len(spb):,} | Kolom: {len(spb.columns)}")
    print(f"Baris WASOP: {len(wasop):,} | Kolom: {len(wasop.columns)}")
    print(f"Baris LHGK: {len(lhgk):,} | Kolom: {len(lhgk.columns)}")

    # --- Merge SPB dan WASOP ---
    spb_key_col = pick_column(spb, "nomor_pkk")
    wasop_key_col = pick_column(wasop, "no_pkk_inaportnet")
    lhgk_key_col = pick_column(lhgk, "no_pkk_inaportnet")

    spb_key = normalize_key_series(spb[spb_key_col])
    wasop_key = normalize_key_series(wasop[wasop_key_col])
    lhgk_key = normalize_key_series(lhgk[lhgk_key_col])

    # Merge WASOP + SPB
    merged = wasop.merge(
        spb,
        how=args.how,
        left_on=wasop_key_col,
        right_on=spb_key_col,
        suffixes=("_spb", "_wasop"),
        indicator=False,
    )

    # Merge hasil di atas dengan LHGK
    merged = merged.merge(
        lhgk,
        how="left",
        left_on=wasop_key_col,
        right_on=lhgk_key_col,
        suffixes=("", "_lhgk"),
        indicator=False,
    )

    # Hapus duplikat berdasarkan no_pkk_inaportnet (kolom utama dari WASOP)
    merged = merged.drop_duplicates(subset=[wasop_key_col], keep="first")

    # Normalisasi key di hasil akhir
    if spb_key_col in merged.columns:
        merged[spb_key_col] = normalize_key_series(merged[spb_key_col])
    if wasop_key_col in merged.columns:
        merged[wasop_key_col] = normalize_key_series(merged[wasop_key_col])
    if lhgk_key_col in merged.columns:
        merged[lhgk_key_col] = normalize_key_series(merged[lhgk_key_col])

    print(f"Hasil merge final: {len(merged):,} baris")

    # Filter: jangan tampilkan data hari ini dikurangi 7 hari sebelumnya, 
    # kecuali kolom nomor_spb tidak kosong
    today = datetime.now().date()
    cutoff = today - timedelta(days=7)
    # Cari kolom tanggal (departure_date, keberangkatan, atau yang mirip)
    date_col = None
    for col in merged.columns:
        if "departure_date" in col.lower() or "keberangkatan" in col.lower():
            date_col = col
            break
    nomor_spb_col = None
    for col in merged.columns:
        if "nomor_spb" in col.lower():
            nomor_spb_col = col
            break
    if date_col:
        def _row_keep(row):
            val = row.get(date_col, "")
            try:
                d = pd.to_datetime(val).date()
            except Exception:
                return True
            if d >= cutoff:
                # Hanya tampilkan jika nomor_spb tidak kosong
                if nomor_spb_col:
                    nomor_spb_val = row.get(nomor_spb_col, "")
                    # Pastikan selalu string sebelum strip
                    if pd.notnull(nomor_spb_val) and str(nomor_spb_val).strip():
                        return True
                return False
            return True
        merged = merged[merged.apply(_row_keep, axis=1)]

    # Setelah proses filter, sebelum simpan ke CSV/Excel, format departure_date ke "YYYY-MM-DD HH:MM"
    date_col = None
    for col in merged.columns:
        if "departure_date" in col.lower() or "keberangkatan" in col.lower():
            date_col = col
            break
    if date_col and date_col in merged.columns:
        def format_datetime(val):
            try:
                # Jika sudah dalam format ISO8601 dengan offset, gunakan strptime
                dt = None
                if isinstance(val, str) and "T" in val and "+" in val:
                    dt = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S%z")
                else:
                    # fallback: parse pakai pandas
                    dt = pd.to_datetime(val)
                if pd.isnull(dt):
                    return ""
                return dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                return val
        merged[date_col] = merged[date_col].apply(format_datetime)

    # Save both CSV and Excel (same stem)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False)
    excel_path = out_path.with_suffix(".xlsx")
    try:
        from pandas.api import types as pdt
        df_xlsx = merged.copy()
        for col in df_xlsx.columns:
            try:
                if pdt.is_datetime64_any_dtype(df_xlsx[col]):
                    if pdt.is_datetime64tz_dtype(df_xlsx[col]):
                        df_xlsx[col] = df_xlsx[col].dt.tz_convert(None)
            except Exception:
                pass
        df_xlsx.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"Tersimpan: {out_path}")
        print(f"Tersimpan: {excel_path}")
    except Exception as e:
        print(f"Warning: gagal menyimpan Excel ({excel_path}): {e}", file=sys.stderr)
        print(f"Hanya CSV tersimpan: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))