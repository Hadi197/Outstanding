import csv
import pandas as pd

def load_csv(file_path):
    """
    Load data from a CSV file.

    :param file_path: Path to the CSV file.
    :return: List of dictionaries representing the rows.
    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f"❌ Failed to load CSV file {file_path}: {e}")
        return []

def save_to_csv(data, output_file):
    """
    Save the given data to a CSV file.

    :param data: List of dictionaries to save.
    :param output_file: Path to the output CSV file.
    """
    if not data:
        print("⚠️ No data to save.")
        return

    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Data successfully saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save data to CSV: {e}")

def lookup_and_merge(wasop_data, spb_data):
    """
    Gabungkan data dari WASOP dan SPB berdasarkan kolom 'no_pkk_inaportnet' dan 'nomor_pkk'.

    :param wasop_data: List of dictionaries dari WASOP.
    :param spb_data: List of dictionaries dari SPB.
    :return: List hasil penggabungan.
    """
    spb_lookup = {row["nomor_pkk"]: row for row in spb_data}
    merged_data = []

    for wasop_row in wasop_data:
        no_pkk_inaportnet = wasop_row.get("no_pkk_inaportnet")
        spb_row = spb_lookup.get(no_pkk_inaportnet)

        if spb_row:
            # Gabungkan data dari kedua tabel
            merged_row = {**wasop_row, **spb_row}
            # Pastikan kolom 'waktu_tolak', 'gt', dan 'loa' masuk ke hasil gabungan
            merged_row["waktu_tolak"] = spb_row.get("waktu_tolak")
            merged_row["gt"] = wasop_row.get("gt")
            merged_row["loa"] = wasop_row.get("loa")
            merged_data.append(merged_row)

    return merged_data

def clean_data(input_file, output_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Remove rows where 'name_process_code' contains 'Nota'
    df = df[~df['name_process_code'].str.contains('Nota', na=False)]

    # Save the cleaned DataFrame back to the CSV file
    df.to_csv(output_file, index=False)
    print(f"Data cleaned and saved to {output_file}")

def modify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Modifikasi DataFrame: drop kolom tertentu dan tambah kolom baru tanpa konversi datetime.
    """
    # Buang kolom yang tidak diperlukan
    columns_to_drop = ["arrive_date_convert", "departure_date_convert", "company_name", "name_branch"]
    df = df.drop(columns=columns_to_drop, errors="ignore")

    # Tambahkan kolom baru dengan nilai default (sesuaikan jika perlu)
    df["waktu_tolak"] = None
    df["gt"] = None
    df["loa"] = None

    return df

def merge_csv_files(wasop_file, spb_file, output_file):
    """
    Gabungkan data tanpa mem-format ulang kolom waktu_tolak (biarkan asli).
    """
    try:
        # Load kedua file CSV
        wasop_df = pd.read_csv(wasop_file)
        spb_df = pd.read_csv(spb_file)

        # Gabungkan berdasarkan kolom 'no_pkk_inaportnet' dan 'nomor_pkk'
        merged_df = pd.merge(wasop_df, spb_df, left_on="no_pkk_inaportnet", right_on="nomor_pkk", how="inner")

        # Ambil hanya kolom yang diperlukan
        selected_columns = [
            "no_pkk", "no_pkk_inaportnet", "nomor_spb", "name_process_code",
            "gt", "loa", "waktu_tolak", "vessel_name"
        ]
        merged_df = merged_df[selected_columns]

        # Simpan hasil gabungan ke file output
        merged_df.to_csv(output_file, index=False)
        print(f"[OK] Data berhasil digabungkan dan disimpan ke: {output_file}")
    except Exception as e:
        print(f"[!] Terjadi kesalahan saat menggabungkan file: {e}")

def main():
    # File paths
    wasop_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/wasop.csv"
    spb_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/spb.csv"
    output_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/gabung.csv"

    # Gabungkan file CSV
    merge_csv_files(wasop_file, spb_file, output_file)

if __name__ == "__main__":
    main()
