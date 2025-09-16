import csv

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

def lookup_and_merge(pkk_data, spb_data):
    """
    Perform a lookup between PKK and SPB data using "no_pkk_inaportnet" and "nomor_pkk".

    :param pkk_data: List of dictionaries from PKK data.
    :param spb_data: List of dictionaries from SPB data.
    :return: Merged list of dictionaries.
    """
    spb_lookup = {row["nomor_pkk"]: row for row in spb_data}
    merged_data = []

    for pkk_row in pkk_data:
        no_pkk_inaportnet = pkk_row.get("no_pkk_inaportnet")
        spb_row = spb_lookup.get(no_pkk_inaportnet)

        if spb_row:
            # Merge the rows
            merged_row = {**pkk_row, **spb_row}
            merged_data.append(merged_row)

    return merged_data

def filter_data(input_file, output_file):
    """
    Filter data based on specific conditions and save to a new CSV file.

    :param input_file: Path to the input CSV file.
    :param output_file: Path to the output CSV file.
    """
    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, \
             open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                # Apply filters
                if row["name_process_code"] != "Nota":
                    writer.writerow(row)

        print(f"✅ Filtered data saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to filter data: {e}")

def filter_pkk_data(input_file, output_file):
    """
    Filter PKK data where "name_process_code" is not equal to "Nota" and save to a new CSV file.

    :param input_file: Path to the input PKK CSV file.
    :param output_file: Path to the output filtered CSV file.
    """
    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, \
             open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                # Apply filter
                if row["name_process_code"] != "Nota":
                    writer.writerow(row)

        print(f"✅ Filtered PKK data saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to filter PKK data: {e}")

def main():
    # File paths
    pkk_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/pkk.csv"
    spb_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/spb.csv"
    filtered_pkk_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/filtered_pkk.csv"
    output_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/gabung.csv"
    filtered_output_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/filtered_gabung.csv"

    # Filter PKK data
    filter_pkk_data(pkk_file, filtered_pkk_file)

    # Load data from CSV files
    pkk_data = load_csv(filtered_pkk_file)
    spb_data = load_csv(spb_file)

    # Perform lookup and merge
    merged_data = lookup_and_merge(pkk_data, spb_data)

    # Save the merged data to a new CSV file
    save_to_csv(merged_data, output_file)

    # Filter the merged data and save to a new CSV file
    filter_data(output_file, filtered_output_file)

if __name__ == "__main__":
    main()
