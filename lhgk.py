import requests
import csv
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time
import os

# tolerant mapping: list of possible source names (prioritized) for each output column
CANDIDATES = {
    "nm_kapal": ["nama_kapal", "NAMA KAPAL", "nm_kapal", "vessel_name", "vessel"],
    "kp_grt": ["grt", "GRT", "kp_grt"],
    "kp_loa": ["loa", "LOA", "kp_loa"],
    "pandu_dari": ["pandu_dari", "DARI", "from", "dari"],
    "pandu_ke": ["pandu_ke", "KE", "to", "ke"],
    "nm_agen": ["nm_agen", "PERUSAHAAN", "agent", "agent_name", "nama_agent"],
    "no_bkt_pandu": ["no_bkt_pandu", "NO SPK PANDU", "no_spk_pandu", "no_spk"],
    "no_pkk_inaportnet": ["no_pkk_inaportnet", "NO PKK INAPORTNET", "no_pkk", "pkk_inaportnet"],
    "no_pkk": ["no_pkk", "NO PKK", "pkk", "nomor_pkk"],
    "nm_pers_pandu": ["nm_pers_pandu", "NAMA PANDU", "nama_pandu", "pandu_name"],
    "mulai_pelaksanaan": ["mulai_pelaksanaan", "MULAI", "mulai", "start", "jam_penetapan_awal"],
    "selesai_pelaksanaan": ["selesai_pelaksanaan", "SELESAI", "selesai", "end", "jam_realisasi_awal"],
    "nm_kapal_1": ["nm_kapal_1", "KAPAL TUNDA 1", "kapal_tunda_1", "tug1", "tugboat1"],
    "nm_kapal_2": ["nm_kapal_2", "KAPAL TUNDA 2", "kapal_tunda_2", "tug2", "tugboat2"],
    "nm_kapal_3": ["nm_kapal_3", "KAPAL TUNDA 3", "kapal_tunda_3", "tug3", "tugboat3"],
    "mulai_tunda": ["mulai_tunda", "MULAI", "mulai_tunda", "start_tow"],
    "selesai_tunda": ["selesai_tunda", "SELESAI", "selesai_tunda", "end_tow"],
    "zone": ["zone", "ZONA", "zona", "pelabuhan", "port"],
    "status_nota": ["status_nota", "STATUS NOTA", "status", "status_verifikasi"]
}

# Rename headers sesuai permintaan sebelum menyimpan
rename_map = {
    "nm_kapal": "NAMA KAPAL",
    "kp_grt": "GT",
    "kp_loa": "LOA",
    "pandu_dari": "DARI",
    "pandu_ke": "KE",
    "nm_agen": "PERUSAHAAN",
    "no_bkt_pandu": "NO SPK PANDU",
    "no_pkk_inaportnet": "NO PKK INAPORTNET",
    "no_pkk": "NO PKK",
    "nm_pers_pandu": "NAMA PANDU",
    "mulai_pelaksanaan": "MULAI PANDU",
    "selesai_pelaksanaan": "SELESAI PANDU",
    "nm_kapal_1": "KAPAL TUNDA 1",
    "nm_kapal_2": "KAPAL TUNDA 2",
    "nm_kapal_3": "KAPAL TUNDA 3",
    "mulai_tunda": "MULAI TUNDA",
    "selesai_tunda": "SELESAI TUNDA",
    "zone": "ZONA",
    "status_nota": "STATUS NOTA"
}

def map_columns(row):
    """Map row data to standardized column names using tolerant mapping."""
    mapped_row = {}
    for output_col, candidate_cols in CANDIDATES.items():
        value = ""
        for candidate in candidate_cols:
            if candidate in row and row[candidate]:
                value = row[candidate]
                break
        mapped_row[output_col] = value
    return mapped_row

API_URL = "https://phinnisi.pelindo.co.id:9014/api/reporting/daily-pilotage/list"

# Get access token from environment variable or fallback to hardcoded value
ACCESS_TOKEN = os.getenv(
    "PHINNISI_ACCESS_TOKEN",
    os.getenv(
        "ACCESS_TOKEN",
        "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMTlwcjd5d0RhdUsxRjFmRHNwUWdmUEhEWFNyNkUxcmJKMGk2ak95QnhzdDRQQVlhWDlqVUdnUXRUVmxvR1l5SE5WeUpVM2FSNVdEcWVKV2VQRFROd3ZUeFdkS3Q2cWtYUUtBQ1VCVk1WQUROYXB6ZFM3WlduYmxrNnRic2N0eldrWlAzQk5hWExjSVNiaW42UkxiVTNmWUtubnVXa2hSQ1hjYTRaWXRyV0RiQUpNTGtpdWxzckFBU2p2WE9waWNjV1NIbVdsMHBUekV2ZWVMd2orMnNHVEZVeWdTOVhVOG5iRGJwSExpdkUxNkYvbTlCbUtBMDNDMGtDWllhb0lBL1loQmxPaEVZYkwwUnFRdmI5YVUweWZtUXJJOXRIWmI4bDNWakViQTJ4ZTlBZ3BCMytReitxSmFGbCtaTldINzJ2bHg3dDl4cWNnbkV1anJ4YTBmQVBDMnp3c3lIbVQzV3dlenQrYzRVOFVUa3QvUjhkMU5jQXBVNmg2SW1XcFRIUUJRZFFucW9Ma0ZYdz09.0V_PiuDEyK7RhOz3aWg6rV5NATp_kcUfqZy7Icb9L_o"
    )
)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
    "access-token": ACCESS_TOKEN,
    "sub-branch": "OTk5,NzU=,NzI=,MTAx,NjE=,ODE=,MjU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,MTc=,NTc=,MTY=,MTA4,NjA=",
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "connection": "keep-alive"
}

def scrap_daily_pilotage(start_date, end_date, page=1, record=1000, max_retries=3):
    params = {
        "start": start_date,
        "end": end_date,
        "data": "",
        "page": page,
        "record": record
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=120)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ReadTimeout as e:
            print(f"Timeout on page {page}, attempt {attempt+1}/{max_retries}")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            print(f"Error on page {page}: {e}")
            if attempt == max_retries - 1:
                raise

# Async version for concurrent requests
async def scrap_daily_pilotage_async(session, start_date, end_date, page=1, record=100000, semaphore=None):
    """Async version for concurrent monthly data fetching"""
    params = {
        "start": start_date,
        "end": end_date,
        "data": "",
        "page": page,
        "record": record
    }

    if semaphore:
        async with semaphore:
            try:
                async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data, start_date, end_date, page
            except Exception as e:
                print(f"Error on {start_date}-{end_date} page {page}: {e}")
                return None, start_date, end_date, page
    else:
        try:
            async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data, start_date, end_date, page
        except Exception as e:
            print(f"Error on {start_date}-{end_date} page {page}: {e}")
            return None, start_date, end_date, page

def month_range(start_date, end_date):
    """Yield (start, end) date string for each month in the period."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start.replace(day=1)
    while current <= end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = (next_month - timedelta(days=1)).day
        period_start = current
        period_end = current.replace(day=last_day)
        if period_end > end:
            period_end = end
        yield period_start.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")
        current = next_month

if __name__ == "__main__":
    # FAST ASYNC VERSION - Process multiple months concurrently
    print("[i] Starting FAST async scraping for all months...")

    async def scrape_all_months_async():
        periods = list(month_range("2025-01-01", "2025-12-31"))
        print(f"[i] Will process {len(periods)} months with concurrent requests...")

        semaphore = asyncio.Semaphore(8)  # Limit concurrent requests to avoid overwhelming the server
        all_data = []

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            start_time = time.time()

            # Create tasks for all months
            tasks = []
            for period_start, period_end in periods:
                # For each month, we need to handle pagination
                task = scrape_month_data_async(session, period_start, period_end, semaphore)
                tasks.append(task)

            # Execute all month tasks concurrently
            print(f"[i] Starting concurrent processing of {len(tasks)} months...")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            print(".2f")

            # Collect all data
            for result in results:
                if isinstance(result, Exception):
                    print(f"[!] Exception in month task: {result}")
                    continue
                if result:
                    all_data.extend(result)

            return all_data

    async def scrape_month_data_async(session, period_start, period_end, semaphore):
        """Scrape all pages for a single month"""
        month_data = []
        page = 1

        while True:
            data, _, _, _ = await scrap_daily_pilotage_async(
                session, period_start, period_end, page=page, record=100000, semaphore=semaphore
            )

            if not data:
                break

            # Cari data tabular pada struktur nested
            rows = None
            if (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], dict)
                and "dataRec" in data["data"]
                and isinstance(data["data"]["dataRec"], list)
            ):
                rows = data["data"]["dataRec"]
            else:
                if isinstance(data, dict):
                    for key in ['dataRec', 'data', 'rows', 'result', 'items']:
                        if key in data and isinstance(data[key], list):
                            rows = data[key]
                            break
                    if rows is None:
                        for key in ['data', 'result', 'items']:
                            if key in data and isinstance(data[key], dict):
                                for subkey in ['dataRec', 'rows', 'items']:
                                    if subkey in data[key] and isinstance(data[key][subkey], list):
                                        rows = data[key][subkey]
                                        break
                                if rows is not None:
                                    break
                elif isinstance(data, list):
                    rows = data

            if rows is not None and len(rows) > 0:
                print(f"  {period_start} s/d {period_end} - Page {page}: {len(rows)} rows")
                month_data.extend(rows)
                if len(rows) < 100000:  # Last page for this month
                    break
                page += 1
            else:
                break

        return month_data

    # Run the async scraping
    all_rows = asyncio.run(scrape_all_months_async())

    print(f"Jumlah total baris ditemukan: {len(all_rows)}")

    if all_rows:
        # Map columns using tolerant mapping
        mapped_rows = []
        for row in all_rows:
            mapped_row = map_columns(row)
            # Filter hanya status_nota = BELUM VERIFIKASI
            if mapped_row.get("status_nota", "").strip().upper() == "BELUM VERIFIKASI":
                # Filter hanya kp_grt > 500
                try:
                    grt_val = float(mapped_row.get("kp_grt", 0))
                except Exception:
                    grt_val = 0
                if grt_val > 500:
                    mapped_rows.append(mapped_row)

        # Hapus duplikat berdasarkan no_pkk_inaportnet (ambil satu saja)
        seen = set()
        unique_rows = []
        for row in mapped_rows:
            key = row.get("no_pkk_inaportnet", "")
            if key and key not in seen:
                seen.add(key)
                unique_rows.append(row)

        # Ambil semua kolom dari CANDIDATES
        selected_cols = list(CANDIDATES.keys())

        # Rename headers sesuai rename_map
        renamed_cols = [rename_map.get(col, col) for col in selected_cols]

        # Rename keys in unique_rows to match renamed_cols
        renamed_rows = []
        for row in unique_rows:
            renamed_row = {}
            for i, col in enumerate(selected_cols):
                renamed_row[renamed_cols[i]] = row.get(col, "")
            renamed_rows.append(renamed_row)

        # Save to current directory (root)
        data_dir = Path(__file__).parent

        csv_path = data_dir / "lhgk.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=renamed_cols)
            writer.writeheader()
            writer.writerows(renamed_rows)
        print(f"Data berhasil disimpan ke {csv_path} (semua kolom mapped, renamed & unik no_pkk_inaportnet)")