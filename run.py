import subprocess
import os
import sys
import pandas as pd

# -----------------------------
# Fungsi untuk menjalankan script Python lain
# -----------------------------
def run_script(script_path):
    try:
        print(f"🚀 Running {script_path}...")
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {os.path.basename(script_path)} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to execute {script_path}: {e}")
    except Exception as e:
        print(f"⚠️ Kesalahan tidak terduga: {e}")

# -----------------------------
# Fungsi untuk membaca CSV dengan path relatif
# -----------------------------
def read_csv_relative(base_dir, file_name):
    file_path = os.path.join(base_dir, file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"✅ Berhasil membaca {file_name}, shape: {df.shape}")
        return df
    else:
        print(f"❌ File {file_name} tidak ditemukan di {file_path}")
        return None

# -----------------------------
# Main function
# -----------------------------
def main():
    # Folder tempat run.py berada
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1️⃣ Jalankan semua script Python lain
    scripts = ["spb.py", "wasop.py", "lookup.py"]
    for script in scripts:
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            run_script(script_path)
        else:
            print(f"❌ Script {script} tidak ditemukan di {base_dir}")

    # 2️⃣ Baca semua CSV di root repo
    csv_files = ["wasop.csv", "gabung.csv", "spb.csv"]
    dataframes = {}
    for csv_file in csv_files:
        df = read_csv_relative(base_dir, csv_file)
        if df is not None:
            dataframes[csv_file] = df

    # 3️⃣ Contoh gabung CSV (wasop.csv + gabung.csv) jika ada kolom 'ID'
    if "wasop.csv" in dataframes and "gabung.csv" in dataframes:
        df_wasop = dataframes["wasop.csv"]
        df_gabung = dataframes["gabung.csv"]

        if "ID" in df_wasop.columns and "ID" in df_gabung.columns:
            df_merged = pd.merge(df_wasop, df_gabung, on="ID", how="outer")
            print("\n✅ Hasil gabung wasop.csv + gabung.csv:")
            print(df_merged.head())

            # Simpan hasil gabungan
            output_file = os.path.join(base_dir, "wasop_gabung.csv")
            df_merged.to_csv(output_file, index=False)
            print(f"✅ File gabungan berhasil disimpan: {output_file}")
        else:
            print("\n❌ Kolom 'ID' tidak ditemukan di kedua CSV. Tidak bisa gabung otomatis.")
    else:
        print("\n❌ Salah satu file CSV untuk gabung tidak ditemukan.")

if __name__ == "__main__":
    main()
        output_file = os.path.join(base_dir, "trafik.csv")
        dataframes["trafik.csv"].to_csv(output_file, index=False)
        print(f"✅ File trafik.csv berhasil di-overwrite: {output_file}")

if __name__ == "__main__":
    main()
