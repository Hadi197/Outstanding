import os
import sys
import subprocess
import csv
import time

def run_script(script_name, base_dir, timeout=600):
    """Run a Python script and stream its output. Return exit code."""
    script_path = os.path.join(base_dir, script_name)
    if not os.path.exists(script_path):
        print(f"Error: required script not found: {script_path}")
        sys.exit(3)

    # Gunakan unbuffered mode (-u) agar output langsung tampil realtime
    cmd = [sys.executable, "-u", script_path]
    print(f"\n>>> Running {script_name} ... (cwd={base_dir})\n")
    sys.stdout.flush()

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        start = time.time()
        last_output = time.time()

        while True:
            line = proc.stdout.readline()
            if line:
                print(line, end="")
                sys.stdout.flush()
                last_output = time.time()
            elif proc.poll() is not None:
                break
            else:
                # Kalau 5 detik tidak ada output, kasih progress dot
                if time.time() - last_output > 5:
                    print(".", end="", flush=True)
                    last_output = time.time()

            if timeout and (time.time() - start) > timeout:
                proc.kill()
                print(f"\nTimeout reached for {script_name}")
                return 124

        proc.wait(timeout=timeout)
        return proc.returncode

    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"\nTimeout expired for {script_name}")
        return 124
    except Exception as e:
        print(f"Error while running {script_name}: {e}")
        return 128


def generate_spb_summary(base_dir):
    """Generate SPB summary and lookup files for dashboard"""
    try:
        import pandas as pd
        import json

        spb_csv_path = os.path.join(base_dir, "spb.csv")
        if not os.path.exists(spb_csv_path):
            print("Warning: spb.csv not found, skipping SPB summary generation")
            return False

        print("\nGenerating SPB summary files for dashboard...")

        # Generate spb_summary.json (total counts)
        spb_df = pd.read_csv(spb_csv_path, usecols=['nomor_pkk'])
        dn_count = spb_df[spb_df['nomor_pkk'].str.contains('PKK.DN', na=False)].shape[0]
        ln_count = spb_df[spb_df['nomor_pkk'].str.contains('PKK.LN', na=False)].shape[0]

        summary = {
            "dn_spb_count": dn_count,
            "ln_spb_count": ln_count,
            "total_spb_count": dn_count + ln_count,
            "last_updated": pd.Timestamp.now().isoformat()
        }

        summary_path = os.path.join(base_dir, "spb_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        # Generate spb_lookup.json (nomor_pkk array for fast lookup)
        nomor_pkk_list = spb_df['nomor_pkk'].dropna().tolist()
        lookup_path = os.path.join(base_dir, "spb_lookup.json")
        with open(lookup_path, 'w') as f:
            json.dump(nomor_pkk_list, f)

        print(f"Generated SPB summary: DN={dn_count}, LN={ln_count}, Total={dn_count + ln_count}")
        print(f"Created {summary_path} and {lookup_path}")
        return True

    except Exception as e:
        print(f"Error generating SPB summary: {e}")
        return False


def concat_csv_files(input_files, output_file):
    """Concatenate CSV files vertically, preserving header from the first file."""
    header_written = False
    written_rows = 0
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as out_f:
            writer = None
            for fpath in input_files:
                if not os.path.exists(fpath):
                    print(f"Warning: input file not found, skipping: {fpath}")
                    continue
                with open(fpath, "r", newline="", encoding="utf-8") as in_f:
                    reader = csv.reader(in_f)
                    rows = list(reader)
                    if not rows:
                        continue
                    header = rows[0]
                    data_rows = rows[1:]
                    if not header_written:
                        writer = csv.writer(out_f)
                        writer.writerow(header)
                        header_written = True
                    if data_rows:
                        writer.writerows(data_rows)
                        written_rows += len(data_rows)
        print(f"\nWrote {written_rows} rows to '{output_file}'.")
        return True
    except Exception as e:
        print(f"Error writing '{output_file}': {e}")
        return False


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Urutan eksekusi sesuai permintaan
    # Include bill.py so billing scraper runs as part of the pipeline
    scripts = ["lhgk.py", "wasop.py", "spb.py", "lookup.py", "bill.py"]
    SCRIPT_TIMEOUT = 1500

    for scr in scripts:
        rc = run_script(scr, base_dir, timeout=SCRIPT_TIMEOUT)
        if rc == 124:
            print(f"\nScript {scr} timeout after {SCRIPT_TIMEOUT} seconds. Aborting.")
            sys.exit(7)
        if rc != 0:
            print(f"\nScript {scr} exited with code {rc}. Aborting.")
            sys.exit(4)

    # Verify required CSV outputs in root folder
    data_dir = base_dir  # Use root directory
    spb_path = os.path.join(data_dir, "spb.csv")
    wasop_path = os.path.join(data_dir, "wasop.csv")
    gabung_path = os.path.join(data_dir, "gabung.csv")
    lhgk_path = os.path.join(data_dir, "lhgk.csv")
    bill_path = os.path.join(data_dir, "bill.csv")

    # Expect lhgk, spb, wasop, and bill outputs to exist after running scripts
    missing = [
        name for name, path in (
            ("lhgk.csv", lhgk_path),
            ("spb.csv", spb_path),
            ("wasop.csv", wasop_path),
            ("bill.csv", bill_path)
        )
        if not os.path.exists(path)
    ]
    if missing:
        print(f"\nError: expected output files missing: {', '.join(missing)}")
        sys.exit(5)

    if not os.path.exists(gabung_path):
        print("\ngabung.csv not found after running scripts — creating gabung.csv by concatenating spb.csv and wasop.csv")
        ok = concat_csv_files([spb_path, wasop_path], gabung_path)
        if not ok:
            print("Failed to create gabung.csv")
            sys.exit(6)
    else:
        print("\ngabung.csv produced by lookup.py")

    # Generate SPB summary files for dashboard
    generate_spb_summary(base_dir)

    print("\nAll done. Outputs available:")
    print(f" - {lhgk_path}")
    print(f" - {wasop_path}")
    print(f" - {spb_path}")
    print(f" - {bill_path}")
    print(f" - {gabung_path}")
    print(f" - spb_summary.json (SPB totals for dashboard)")
    print(f" - spb_lookup.json (SPB lookup data for dashboard)")


if __name__ == "__main__":
    main()
