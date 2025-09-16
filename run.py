import subprocess

def run_script(script_name):
    """
    Run a Python script using subprocess.

    :param script_name: The name of the script to run.
    """
    try:
        print(f"🚀 Running {script_name}...")
        subprocess.run(["python3", script_name], check=True)
        print(f"✅ {script_name} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to execute {script_name}: {e}")

def main():
    # Define the scripts to run
    scripts = [
        "pkk.py",  # Updated from pmh.py to pkk.py
        "spb.py",
        "lookup.py"
    ]

    # Base directory for the scripts
    base_dir = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP"

    # Run each script
    for script in scripts:
        script_path = f"{base_dir}/{script}"
        run_script(script_path)

if __name__ == "__main__":
    main()
