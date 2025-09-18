import pandas as pd

# Baca file, header tabel mulai dari baris ke-3 (index=2)
df = pd.read_excel("PRODUKSI_REGIONAL 3 TANJUNG PERAK (13).xlsx", 
                   sheet_name="TRAFFIC", header=2)

# Cari kolom yang ada kata DATE, TIME, atau AT
datetime_cols = [col for col in df.columns 
                 if any(x in str(col).upper() for x in ["DATE", "TIME", "AT"])]

# Konversi ke datetime
for col in datetime_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

# Simpan hasil ke Excel baru
df.to_excel("PRODUKSI_REGIONAL3_TANJUNGPERAK_CLEAN.xlsx", 
            sheet_name="TRAFFIC", index=False)

print("Kolom datetime yang dikonversi:", datetime_cols)
