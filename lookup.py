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

def lookup_and_extract(pkk_data, spb_data):
    """
    Perform a lookup between PKK and SPB data using "no_pkk_inaportnet" and "nomor_pkk",
    and extract specific columns.

    :param pkk_data: List of dictionaries from PKK data.
    :param spb_data: List of dictionaries from SPB data.
    :return: Extracted and merged list of dictionaries.
    """
    spb_lookup = {row["nomor_pkk"]: row for row in spb_data}
    extracted_columns = [
        "no_pkk",
        "no_pkk_inaportnet",
        "arrive_date_convert",
        "departure_date_convert",
        "vessel_name",
        "name_process_code",
        "company_name",
        "name_branch",
        "nomor_spb"
    ]
    merged_data = []

    for pkk_row in pkk_data:
        no_pkk_inaportnet = pkk_row.get("no_pkk_inaportnet")
        spb_row = spb_lookup.get(no_pkk_inaportnet)

        if spb_row:
            # Merge the rows and extract specific columns
            merged_row = {col: pkk_row.get(col, spb_row.get(col)) for col in extracted_columns}
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

def main():
    # File paths
    pkk_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/pkk.csv"
    spb_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/spb.csv"
    output_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/gabung.csv"

    # Load data from CSV files
    pkk_data = load_csv(pkk_file)
    spb_data = load_csv(spb_file)

    # Perform lookup and extract specific columns
    merged_data = lookup_and_extract(pkk_data, spb_data)

    # Save the merged data to a new CSV file
    save_to_csv(merged_data, output_file)

    # Clean the merged data
    clean_data(output_file, output_file)

if __name__ == "__main__":
    main()
