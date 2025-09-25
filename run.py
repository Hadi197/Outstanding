import os
import sys
import subprocess
import csv
import time

def run_script_stream(script_path, cwd, timeout=None):
    """Run a Python script with the same interpreter, stream its stdout+stderr, return rc."""
    cmd = [sys.executable, script_path]
    print(f"\n>>> Running: {' '.join(cmd)} (cwd={cwd})\n")
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        print(f"Failed to start {script_path}: {e}")
        return 127

    start = time.time()
    try:
        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            print(line, end="")
            if timeout and (time.time() - start) > timeout:
                proc.kill()
                print(f"\nTimeout reached for {script_path}")
                return 124
        proc.wait(timeout=timeout)
        return proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"\nTimeout expired for {script_path}")
        return 124
    except Exception as e:
        try:
            proc.kill()
        except Exception:
            pass
        print(f"Error while running {script_path}: {e}")
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
    # Urutan eksekusi: spb.py, wasop.py, lhgk.py, lookup.py
    scripts = ["spb.py", "wasop.py", "lhgk.py", "lookup.py"]
    expected = {"spb.py": "spb.csv", "wasop.py": "wasop.csv", "lhgk.py": "lhgk.csv", "lookup.py": "gabung.csv"}

    SCRIPT_TIMEOUT = 600

    for scr in scripts:
        scr_path = os.path.join(base_dir, scr)
        if not os.path.exists(scr_path):
            print(f"Error: required script not found: {scr_path}")
            sys.exit(3)
        rc = run_script_stream(scr_path, cwd=base_dir, timeout=SCRIPT_TIMEOUT)
        if rc == 124:
            print(f"\nScript {scr} timeout after {SCRIPT_TIMEOUT} seconds. Aborting.")
            sys.exit(7)
        if rc != 0:
            print(f"\nScript {scr} exited with code {rc}. Aborting.")
            sys.exit(4)

    # Verify required CSV outputs
    spb_path = os.path.join(base_dir, "spb.csv")
    wasop_path = os.path.join(base_dir, "wasop.csv")
    gabung_path = os.path.join(base_dir, "gabung.csv")
    lhgk_path = os.path.join(base_dir, "lhgk.csv")

    missing = [name for name, path in (("lhgk.csv", lhgk_path), ("spb.csv", spb_path), ("wasop.csv", wasop_path)) if not os.path.exists(path)]
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

