# /Users/hadipurwana/Documents/PYTHON/OUT ALL/lookup.py
import argparse
from pathlib import Path
import sys
import pandas as pd


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

    parser = argparse.ArgumentParser(
        description="Gabungkan SPB.csv (kolom: nomor_pkk) dengan wasop.csv (kolom: no_pkk_inaportnet)."
    )
    parser.add_argument("--spb", help="Path ke SPB.csv (default: cari di direktori skrip)")
    parser.add_argument("--wasop", help="Path ke wasop.csv (default: cari di direktori skrip)")
    parser.add_argument("--how", choices=["left", "right", "inner", "outer"], default="left",
                        help="Tipe merge (default: left, WASOP sebagai referensi)")
    parser.add_argument("--output", "-o", help="Path output CSV (default: gabung.csv di direktori skrip)")
    args = parser.parse_args(argv)

    spb_path = resolve_path(args.spb, ["SPB.csv", "spb.csv"], here)
    wasop_path = resolve_path(args.wasop, ["wasop.csv", "WASOP.csv"], here)
    out_path = Path(args.output) if args.output else (here / "gabung.csv")

    print(f"Memuat SPB: {spb_path}")
    print(f"Memuat WASOP: {wasop_path}")

    # Load as string to preserve PKK formatting
    spb = pd.read_csv(spb_path, dtype=str, keep_default_na=False)
    wasop = pd.read_csv(wasop_path, dtype=str, keep_default_na=False)

    print(f"Baris SPB: {len(spb):,} | Kolom: {len(spb.columns)}")
    print(f"Baris WASOP: {len(wasop):,} | Kolom: {len(wasop.columns)}")

    spb_key_col = pick_column(spb, "nomor_pkk")
    wasop_key_col = pick_column(wasop, "no_pkk_inaportnet")

    spb_key = normalize_key_series(spb[spb_key_col])
    wasop_key = normalize_key_series(wasop[wasop_key_col])

    # Use indicator to report match stats (WASOP as left, SPB as right)
    merged = wasop.merge(
        spb,
        how=args.how,
        left_on=wasop_key,
        right_on=spb_key,
        suffixes=("_spb", "_wasop"),
        indicator=True,
    )

    # Re-do merge cleanly using column names to keep keys (WASOP left)
    merged = wasop.merge(
        spb,
        how=args.how,
        left_on=wasop_key_col,
        right_on=spb_key_col,
        suffixes=("_spb", "_wasop"),
        indicator=True,
    )

    # Normalize keys in the merged result (optional, for consistency)
    if spb_key_col in merged.columns:
        merged[spb_key_col] = normalize_key_series(merged[spb_key_col])
    if wasop_key_col in merged.columns:
        merged[wasop_key_col] = normalize_key_series(merged[wasop_key_col])

    # Report stats
    left_only = (merged["_merge"] == "left_only").sum() if "_merge" in merged.columns else 0
    right_only = (merged["_merge"] == "right_only").sum() if "_merge" in merged.columns else 0
    both = (merged["_merge"] == "both").sum() if "_merge" in merged.columns else len(merged)

    print(f"Hasil merge: {len(merged):,} baris")
    print(f"- Cocok di kedua sisi: {both:,}")
    if args.how in ("left", "outer"):
        print(f"- Hanya di WASOP (left_only): {left_only:,}")
    if args.how in ("right", "outer"):
        print(f"- Hanya di SPB (right_only): {right_only:,}")

    # Filter: tampilkan baris dengan SPB kosong dan departure_date > 7 hari dari hari ini
    # atau baris dengan SPB tidak kosong
    nomor_spb_series = merged["nomor_spb"] if "nomor_spb" in merged.columns else pd.Series([None] * len(merged))
    spb_empty = nomor_spb_series.isna() | (nomor_spb_series.astype(str).str.strip() == "")
    spb_not_empty = ~spb_empty

    # Normalize departure_date and today to be timezone-naive
    dep_dt = pd.to_datetime(merged.get("departure_date"), errors="coerce").dt.tz_localize(None)
    today = pd.Timestamp.today().normalize().tz_localize(None)

    age_days = (today - dep_dt).dt.days
    older_than_7 = age_days > 7

    # Combine conditions: SPB kosong dan departure_date > 7 hari, atau SPB tidak kosong
    mask = (spb_empty & older_than_7) | spb_not_empty
    merged = merged[mask].copy()

    # Hapus kolom indikator sebelum simpan jika tidak diperlukan
    if "_merge" in merged.columns:
        merged = merged.drop(columns=["_merge"])

    # Save both CSV and Excel (same stem)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 1) CSV
    merged.to_csv(out_path, index=False)

    # 2) XLSX (same stem as out_path)
    excel_path = out_path.with_suffix(".xlsx")
    try:
        # Make a copy and normalize timezone-aware datetimes (if any) for Excel compatibility
        df_xlsx = merged.copy()
        # Use pandas type utilities to detect datetime columns robustly
        from pandas.api import types as pdt
        for col in df_xlsx.columns:
            try:
                if pdt.is_datetime64_any_dtype(df_xlsx[col]):
                    # If tz-aware, convert to naive; otherwise leave as-is
                    if pdt.is_datetime64tz_dtype(df_xlsx[col]):
                        df_xlsx[col] = df_xlsx[col].dt.tz_convert(None)
            except Exception:
                # Ignore conversion errors for safety (keep original data)
                pass
        # Write Excel (pandas will use openpyxl if available)
        df_xlsx.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"Tersimpan: {out_path}")
        print(f"Tersimpan: {excel_path}")
    except Exception as e:
        # If Excel write fails, keep CSV and warn
        print(f"Warning: gagal menyimpan Excel ({excel_path}): {e}", file=sys.stderr)
        print(f"Hanya CSV tersimpan: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))