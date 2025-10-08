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
    scripts = ["lhgk.py", "wasop.py", "spb.py", "lookup.py"]
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

    missing = [
        name for name, path in (
            ("lhgk.csv", lhgk_path),
            ("spb.csv", spb_path),
            ("wasop.csv", wasop_path)
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

    print("\nAll done. Outputs available:")
    print(f" - {lhgk_path}")
    print(f" - {wasop_path}")
    print(f" - {spb_path}")
    print(f" - {gabung_path}")


if __name__ == "__main__":
    main()
