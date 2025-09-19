import subprocess
import os

def run_script(script_path):
    """
    Run a Python script using subprocess.
    """
    try:
        print(f"🚀 Running {script_path}...")
        subprocess.run(["python3", script_path], check=True)
        print(f"✅ {os.path.basename(script_path)} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to execute {script_path}: {e}")
    except Exception as e:
        print(f"⚠️ Kesalahan tidak terduga: {e}")

def main():
    # cari path folder tempat run.py berada
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the scripts to run (pakai relative, otomatis cari di folder yg sama dengan run.py)
    scripts = [
        "spb.py",
        "wasop.py",
        "lookup.py",
    ]

    for script in scripts:
        script_path = os.path.join(base_dir, script)
        run_script(script_path)

if __name__ == "__main__":
    main()
